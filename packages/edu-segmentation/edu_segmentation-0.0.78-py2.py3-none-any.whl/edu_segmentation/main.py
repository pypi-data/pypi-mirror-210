from .BARTTokenClassification.run_segbot_bart import run_segbot_bart
from .BERTTokenClassification.run_bert import run_segbot_bert

def run_segbot(sent, granularity_level="default", model="bart"):
    print("----------- EDU Segmentation with Segbot with BART model: ----------")
    results = []

    segbot_model = run_segbot_bart
    if model == "bert_uncased":
        segbot_model = run_segbot_bert
    elif model == "bert_cased":
        # segbot_model = run_segbot_bert
        pass

    if granularity_level == "conjunction_words":
        print("Conjunction words are removed from the sentence, then each segment is passed EDU-segmented.")
        conjunctions = [
            "and",
            "however",
            "but",
            "or",
            "so",
            "for",
            "nor",
            "yet",
            "after",
            "although",
            "as",
            "because",
            "before",
            "if",
            "once",
            "since",
            "than",
            "that",
            "though",
            "till",
            "unless",
            "until",
            "when",
            "where",
            "whether",
            "while",
        ]
        segments = []
        current_segment = []
        words = sent.split()

        for word in words:
            if word.lower() in conjunctions:
                if current_segment:
                    segments.append(" ".join(current_segment))
                current_segment.clear()
            else:
                current_segment.append(word)

        if current_segment:
            segments.append(" ".join(current_segment))
        for word in segments:
            results.append(segbot_model(word))
    else:
        results.append(segbot_model(sent))
    return results

