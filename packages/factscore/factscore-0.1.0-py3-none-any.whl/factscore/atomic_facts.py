import json
import numpy as np
import re
import functools
import string
import spacy
import sys
from tqdm import tqdm
import openai
from rank_bm25 import BM25Okapi
import os
import time
from nltk.tokenize import sent_tokenize


class AtomicFactGenerator(object):
    def __init__(self, key_path, demon_dir, model_name=None, gpt3_cache_dir=None):

        self.model = model_name
        if model_name:
            self.preprocess_fn = functools.partial(preprocess_fn, model=model_name)
        else:
            self.preprocess_fn = None
        self.nlp = spacy.load("en_core_web_sm")
        self.key_path = key_path
        self.is_bio = True
        self.demon_path = os.path.join(demon_dir, "demons.json" if self.is_bio else "demons_complex.json")
        if gpt3_cache_dir is not None:
            self.gpt3_cache_path = os.path.join(gpt3_cache_dir, "{}_{}_additional.json".format("bio" if self.is_bio else "complex", model_name))
        else:
            self.gpt3_cache_path = None

        # load api key
        with open(key_path, 'r') as f:
            api_key = f.readline()
        openai.api_key = api_key.strip()

        # get the demos
        with open(self.demon_path, 'r') as f:
            self.demons = json.load(f)

        tokenized_corpus = [doc.split(" ") for doc in self.demons.keys()]
        self.bm25 = BM25Okapi(tokenized_corpus)

    def run(self, generation):
        """Convert the generation into a set of atomic facts."""
        if self.preprocess_fn:
            paragraphs = self.preprocess(generation)
        else:
            paragraphs = [para.strip() for para in generation.split("\n") if len(para.strip()) > 0]

        atomic_facts, para_breaks = self.get_atomic_facts_from_paragraph(paragraphs)
        return atomic_facts, para_breaks

    def get_atomic_facts_from_paragraph(self, paragraphs):
        sentences = []
        para_breaks = []
        for para_idx, paragraph in enumerate(paragraphs):
            if para_idx > 0 :
                para_breaks.append(len(sentences))

            initials = detect_initials(paragraph)

            curr_sentences = sent_tokenize(paragraph)
            curr_sentences_2 = sent_tokenize(paragraph)

            curr_sentences = fix_sentence_splitter(curr_sentences, initials)
            curr_sentences_2 = fix_sentence_splitter(curr_sentences_2, initials)

            # checking this, just to ensure the crediability of the sentence splitter fixing algorithm
            assert curr_sentences == curr_sentences_2, (paragraph, curr_sentences, curr_sentences_2)

            sentences += curr_sentences

        atoms = self.get_init_atomic_facts_from_sentence([sent for i, sent in enumerate(sentences) if not (not self.is_bio and ( \
                    (i==0 and (sent.startswith("Sure") or sent.startswith("Here are"))) or \
                    (i==len(sentences)-1 and (sent.startswith("Please") or sent.startswith("I hope") or sent.startswith("Here are")))))])

        atomic_facts_pairs = []
        for i, sent in enumerate(sentences):
            if not self.is_bio and ( \
                (i==0 and (sent.startswith("Sure") or sent.startswith("Here are"))) or \
                (i==len(sentences)-1 and (sent.startswith("Please") or sent.startswith("I hope") or sent.startswith("Here are")))):
                atomic_facts_pairs.append((sent, []))
            elif self.is_bio and sent.startswith("This sentence does not contain any facts"):
                atomic_facts_pairs.append((sent, []))
            elif sent.startswith("Sure") or sent.startswith("Please") or (i==0 and sent.startswith("Here are")):
                atomic_facts_pairs.append((sent, []))
            else:
                atomic_facts_pairs.append((sent, atoms[sent]))

        # postprocess_atomic_facts will fix minor issues from InstructGPT
        # it is supposed to handle sentence splitter issue too, but since here
        # we fixed sentence splitter issue already,
        # the new para_breaks should be identical to the original para_breaks
        if self.is_bio:
            atomic_facts_pairs, para_breaks = postprocess_atomic_facts(atomic_facts_pairs, list(para_breaks), self.nlp)

        return atomic_facts_pairs, para_breaks


    def get_init_atomic_facts_from_sentence(self, sentences):
        is_bio = self.is_bio
        demons = self.demons

        k = 1 if is_bio else 0
        n = 7 if is_bio else 8
        batch_size = 8

        prompts = []
        prompt_to_sent = {}
        atoms = {}
        for sentence in sentences:
            if sentence in atoms:
                continue
            top_machings = best_demos(sentence, self.bm25, list(demons.keys()), k)
            prompt = ""

            for i in range(n):
                prompt = prompt + "Please breakdown the following sentence into independent facts: {}\n".format(list(demons.keys())[i])
                for fact in demons[list(demons.keys())[i]]:
                    prompt = prompt + "- {}\n".format(fact)
                prompt = prompt + "\n"

            for match in top_machings:
                prompt = prompt + "Please breakdown the following sentence into independent facts: {}\n".format(match)
                for fact in demons[match]:
                    prompt = prompt + "- {}\n".format(fact)
                prompt = prompt + "\n"
            prompt = prompt + "Please breakdown the following sentence into independent facts: {}\n".format(sentence)
            prompts.append(prompt)
            prompt_to_sent[prompt] = sentence

        for i in range(0, len(prompts), batch_size):
            response = call_gpt3(prompts[i: i+batch_size])
            for j in range(len(response["choices"])):
                atoms[prompt_to_sent[prompts[i+j]]] = text_to_sentences(response["choices"][j]["text"])
            
        for key, value in demons.items():
            if key not in atoms:
                atoms[key] = value

        return atoms


def preprocess_fn(generation, model):
    if model in ["instruct", "gpt4", "vicuna-7b", "vicuna-13b", "chatgpt"]:
        if not generation.startswith("I'm sorry") and not "provide more" in generation:
            paragraphs = [para.strip() for para in generation.split("\n") if len(para.strip()) > 0]
        else:
            return None

    elif model == "perplexity":
        output = remove_citation(generation)
        if is_invalid_ppl(output):
            return None
        paragraphs = []
        for para in output.split("\n\n"):
            if is_invalid_paragraph_ppl(para):
                break
            paragraphs.append(para.strip())
        
        if len(paragraphs) == 0:
            return None

    elif model in ["mpt-7b", "stablelm-alpha-7b"]:
        if not "sorry" in generation and not "provide" in generation.split(" "):
            paragraphs = [para.strip() for para in generation.split("\n") if len(para.strip()) > 0]

    else:
        paragraphs = [para.strip() for para in generation.split("\n") if len(para.strip()) > 0]
    
    return paragraphs


def call_gpt3(prompt, model_name="text-davinci-003", max_len=512, temp=0.7, num_log_probs=0, echo=False):
    # call GPT-3 API until result is provided and then return it
    response = None
    received = False

    while not received:
        try:
            response = openai.Completion.create(model=model_name,
                                                prompt=prompt,
                                                max_tokens=max_len,
                                                temperature=temp,
                                                logprobs=num_log_probs,
                                                echo=echo)
            received = True
        except:
            error = sys.exc_info()[0]
            if error == openai.error.InvalidRequestError:
                # something is wrong: e.g. prompt too long
                print(f"InvalidRequestError\nPrompt passed in:\n\n{prompt}\n\n")
                assert False
            print("API error:", error)
            time.sleep(1)
    return response

def best_demos(query, bm25, demons_sents, k):
    tokenized_query = query.split(" ")
    top_machings = bm25.get_top_n(tokenized_query, demons_sents, k)
    return top_machings


# transform InstructGPT output into sentences
def text_to_sentences(text):
    sentences = text.split("- ")[1:]
    sentences = [sent.strip()[:-1] if sent.strip()[-1] == '\n' else sent.strip() for sent in sentences]
    if len(sentences) > 0: 
        if sentences[-1][-1] != '.':
            sentences[-1] = sentences[-1] + '.' 
    else:
        sentences = []
    return sentences


def normalize_answer(s):
    """Lower text and remove punctuation, articles and extra whitespace."""
    def remove_articles(text):
        regex = re.compile(r'\b(a|an|the)\b', re.UNICODE)
        return re.sub(regex, ' ', text)
    def white_space_fix(text):
        return ' '.join(text.split())
    def remove_punc(text):
        exclude = set(string.punctuation)
        return ''.join(ch for ch in text if ch not in exclude)
    def lower(text):
        return text.lower()
    return white_space_fix(remove_articles(remove_punc(lower(s))))

MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
MONTHS = [m.lower() for m in MONTHS]

def is_num(text):
    try:
        text = int(text)
        return True
    except Exception:
        return False

def is_date(text):
    text = normalize_answer(text)
    for token in text.split(" "):
        if (not is_num(token)) and token not in MONTHS:
            return False
    return True

def extract_numeric_values(text):
    pattern = r'\b\d+\b'  # regular expression pattern for integers
    numeric_values = re.findall(pattern, text)  # find all numeric values in the text
    return set([value for value in numeric_values])  # convert the values to float and return as a list


def detect_entities(text, nlp):
    doc = nlp(text)
    entities = set()

    def _add_to_entities(text):
        if "-" in text:
            for _text in text.split("-"):
                entities.add(_text.strip())
        else:
            entities.add(text)


    for ent in doc.ents:
        # spacy often has errors with other types of entities
        if ent.label_ in ["DATE", "TIME", "PERCENT", "MONEY", "QUANTITY", "ORDINAL", "CARDINAL"]:

            if is_date(ent.text):
                _add_to_entities(ent.text)
            else:
                for token in ent.text.split():
                    if is_date(token):
                        _add_to_entities(token)
        
    for new_ent in extract_numeric_values(text):
        if not np.any([new_ent in ent for ent in entities]):
            entities.add(new_ent)

    return entities

def postprocess_atomic_facts(_atomic_facts, para_breaks, nlp):

    verbs = ["born.", " appointed.", " characterized.", " described.", " known.", " member.", " advocate.", "served.", "elected."]
    permitted_verbs = ["founding member."]

    atomic_facts = []
    new_atomic_facts = []
    new_para_breaks = []
    
    for i, (sent, facts) in enumerate(_atomic_facts):
        sent = sent.strip()
        if len(sent.split())==1 and i not in para_breaks and i > 0:
            assert i not in para_breaks
            atomic_facts[-1][0] += " " + sent
            atomic_facts[-1][1] += facts
        else:
            if i in para_breaks:
                new_para_breaks.append(len(atomic_facts))
            atomic_facts.append([sent, facts])

    for i, (sent, facts) in enumerate(atomic_facts):
        entities = detect_entities(sent, nlp)
        covered_entities = set()
        # print (entities)
        new_facts = []
        for i, fact in enumerate(facts):
            if any([fact.endswith(verb) for verb in verbs]) and not any([fact.endswith(verb) for verb in permitted_verbs]):
                if any([fact[:-1] in other_fact for j, other_fact in enumerate(facts) if j != i]):
                    continue
            sent_entities = detect_entities(fact, nlp)
            covered_entities |= set([e for e in sent_entities if e in entities])
            new_entities = sent_entities - entities
            if len(new_entities) > 0:
                do_pass = False
                for new_ent in new_entities:
                    pre_ent = None
                    for ent in entities:
                        if ent.startswith(new_ent):
                            pre_ent = ent
                            break			
                    if pre_ent is None:
                        do_pass = True
                        break
                    fact = fact.replace(new_ent, pre_ent)
                    covered_entities.add(pre_ent)
                if do_pass:
                    continue
            if fact in new_facts:
                continue
            new_facts.append(fact)
        try:
            assert entities==covered_entities
        except Exception:
            new_facts = facts # there is a bug in spacy entity linker, so just go with the previous facts
        
        new_atomic_facts.append((sent, new_facts))
    
    return new_atomic_facts, new_para_breaks

def is_integer(s):
    try:
        s = int(s)
        return True
    except Exception:
        return False

def remove_citation(text):
    # text = re.sub(r'\[\d+\]', '', text)
    text = re.sub(r"\s*\[\d+\]\s*","", text)
    if text.startswith("According to , "):
        text = text.replace("According to , ", "According to the search results, ")
    return text

invalid_ppl_mentions = [
    "I could not find any information",
    "The search results do not provide",
    "There is no information",
    "There are no search results",
    "there are no provided search results",
    "not provided in the search results",
    "is not mentioned in the provided search results",
    "There seems to be a mistake in the question",
    "Not sources found",
    "Try a more general question"
]

def is_invalid_ppl(text):
    return np.any([text.lower().startswith(mention.lower()) for mention in invalid_ppl_mentions])

def is_invalid_paragraph_ppl(text):
    return len(text.strip())==0 or np.any([mention.lower() in text.lower() for mention in invalid_ppl_mentions])

def detect_initials(text):
    pattern = r"[A-Z]\. ?[A-Z]\."
    match = re.findall(pattern, text)
    return [m for m in match]

def fix_sentence_splitter(curr_sentences, initials):
    for initial in initials:
        if not np.any([initial in sent for sent in curr_sentences]):
            alpha1, alpha2 = [t.strip() for t in initial.split(".") if len(t.strip())>0]
            for i, (sent1, sent2) in enumerate(zip(curr_sentences, curr_sentences[1:])):
                if sent1.endswith(alpha1 + ".") and sent2.startswith(alpha2 + "."):
                    # merge sentence i and i+1
                    curr_sentences = curr_sentences[:i] + [curr_sentences[i] + " " + curr_sentences[i+1]] + curr_sentences[i+2:]
                    break
    sentences = []
    combine_with_previous = None
    for sent_idx, sent in enumerate(curr_sentences):
        if len(sent.split())<=1 and sent_idx==0:
            assert not combine_with_previous
            combine_with_previous = True
            sentences.append(sent)
        elif len(sent.split())<=1:
            assert sent_idx > 0
            sentences[-1] += " " + sent
            combined_with_previous = False
        elif sent[0].isalpha() and not sent[0].isupper() and sent_idx > 0:
            assert sent_idx > 0, curr_sentences
            sentences[-1] += " " + sent
            combine_with_previous = False
        elif combine_with_previous:
            assert sent_idx > 0
            sentences[-1] += " " + sent
            combine_with_previous = False
        else:
            assert not combine_with_previous
            sentences.append(sent)
    return sentences


def main():
    generator = AtomicFactGenerator("api.key", "demos", model_name=None, gpt3_cache_dir=None)
    atomic_facts, para_breaks = generator.run("Thierry Henry (born 17 August 1977) is a French professional football coach, pundit, and former player. He is considered one of the greatest strikers of all time, and one the greatest players of the Premier League history. He has been named Arsenal F.C's greatest ever player.\n\nHenry made his professional debut with Monaco in 1994 before signing for defending Serie A champions Juventus. However, limited playing time, coupled with disagreements with the club's hierarchy, led to him signing for Premier League club Arsenal for £11 million in 1999.")

    print(atomic_facts)
    print(para_breaks)

if __name__ == "__main__":
    main()