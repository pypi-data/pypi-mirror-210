def benchmark(sentences, base_model, tiny_model):
    base_correct = tiny_correct = 0
    total = len(sentences)


    for sentence, correct in sentences:
        print(sentence)
        correct_sentence = sentence.replace('[MASK]', correct).lower()

        base_prediction = base_model(sentence)[0]['sequence']
        tiny_prediction = tiny_model(sentence)[0]['sequence']

        print(tiny_prediction)
        print(base_prediction)

        base_correct += int(base_prediction == correct_sentence)
        tiny_correct += int(tiny_prediction == correct_sentence)
    
    return tiny_correct / total, base_correct / total
