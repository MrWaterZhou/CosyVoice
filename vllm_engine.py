from vllm import LLM, SamplingParams
import json
import os
import re
import torch
import numpy as np

pattern = re.compile(r"<\|speech-(\d+)\|>")


class OfflineInference:
    def __init__(self, model_path):
        self.bias = torch.load(os.path.join(model_path, 'bias.tensor')).to(torch.bfloat16)

        def process_token(token_ids, logits):
            logits = logits + self.bias
            return logits

        stop = ["<|cos_eos|>"]
        tensor_parallel_size = 1
        max_tokens = 4096
        self.sampling_params = SamplingParams(temperature=0.0, best_of=1, stop=stop,
                                              max_tokens=max_tokens, repetition_penalty=1.3, n=1,
                                              logits_processors=[process_token])
        self.model = LLM(model=model_path,
                         tokenizer=model_path,
                         trust_remote_code=True,
                         tensor_parallel_size=tensor_parallel_size,
                         dtype='bfloat16',
                         max_model_len=max_tokens,
                         )

    def batch_infer(self, text_ids_list, prompt_speech_token_list):
        prompts = [[151936] + text_ids + [151937] + [x + 151938 for x in prompt_speech_token] for
                   text_ids, prompt_text_ids, prompt_speech_token in
                   zip(text_ids_list, prompt_speech_token_list)]

        outputs = self.model.generate(prompts, self.sampling_params)
        results = []
        for output in outputs:
            generated_text = output.outputs[0].text
            snac_tokens = pattern.findall(generated_text)
            snac_tokens = [int(x) for x in snac_tokens]
            results.append(snac_tokens)
        return results


if __name__ == '__main__':
    model = OfflineInference('pretrained_models/CosyVoice2-0.5B/merged')
    text_ids_list = [[32664, 1773, 77288, 35946, 99680, 99408, 21894, 16530, 18493,
                      99587, 1773, 99517, 39165, 13343, 31235, 18493, 99587, 9370,
                      29826, 99261, 3837, 80158, 20412, 18830, 14777, 35727, 35946,
                      99962, 30440, 23031, 99372, 99838, 3837, 60894, 33447, 103086,
                      103086, 99865, 99865, 29490, 99227, 14777, 82224, 99838, 99748,
                      107519, 99517, 1773, 35946, 99962, 39165, 7948, 74763, 20412,
                      43288, 81596, 99590, 50511, 99517, 9370, 1773, 50009, 26939,
                      52801, 97815, 45181, 99427, 23384, 101400, 36407, 9370, 21287,
                      8903, 99748, 52853, 3837, 99212, 69442, 36589, 47815, 9370,
                      99851, 99370, 57218, 99194, 99194, 9370, 100549, 99477, 99258,
                      35946, 63109, 15946, 99356, 99333, 34187, 100475, 100576, 9370,
                      99234, 99350, 3837, 48738, 36629, 29524, 99232, 99261, 99791,
                      103412, 53222, 1773]]
    prompt_speech_token_list = [[1573, 2166, 138, 5096, 398, 35, 733, 733, 732, 1704, 2112, 2112,
                                 4299, 4299, 4299, 4299, 4299, 4299, 2112, 1704, 3645, 3645, 5832, 5859,
                                 3675, 3648, 3645, 3645, 3645, 1458, 2112, 4299, 4299, 2166, 63, 4484,
                                 4979, 3590, 584, 578, 1884, 1793, 5914, 1092, 183, 4519, 6501, 3584,
                                 668, 2148, 1443, 1280, 6378, 3465, 4487, 5188, 3002, 524, 573, 570,
                                 1456, 1367, 598, 1300, 2112, 4299, 4299, 4299, 4299, 4299, 4299, 4299,
                                 4299, 4299, 4299, 4299, 4299, 4299, 4299, 4299, 4299, 4299, 4299, 4299,
                                 4299, 4299, 2112, 1842, 2916, 5113, 225, 297, 4457, 5071, 6448, 5949,
                                 6048, 1535, 882, 5001, 2421, 4597, 4523, 1284, 4923, 5, 326, 2760,
                                 2841, 2912, 1044, 74, 3047, 6021, 6291, 127, 920, 3080, 1892, 1649,
                                 1657, 1620, 4299, 4299, 4299, 4299, 4299, 4299, 4299, 4299, 4299, 4299,
                                 4299, 4299, 4299, 2112, 2463, 4839, 3157, 6311, 5896, 6057, 3077, 3481,
                                 404, 1433, 2093, 1616, 4940, 960, 57, 2760, 4633, 4487, 2884, 3590,
                                 575, 1434, 2163, 3728, 5834, 468, 489, 405, 3012, 5102, 5075, 647,
                                 877, 1611, 404, 1052, 523, 2760, 2841, 2775, 4682, 4448, 3178, 2028,
                                 3972, 2112, 4299, 4299, 4299, 2031, 3891, 5832, 5832, 5835, 5859, 5862,
                                 5943, 3729, 1542, 1542, 1785, 2112, 2028, 1657, 929, 5589, 5035, 2897,
                                 2717, 4944, 2779, 5048, 5776, 4875, 5776, 5048, 6040, 3720, 4849, 4570,
                                 3151, 4534, 62, 873, 306, 1188, 1440, 5996, 2366, 2321, 942, 6051,
                                 810, 1217, 503, 2841, 2766, 4745, 5986, 2240, 5100, 1203, 546, 6055,
                                 6027, 1699, 1610, 1920, 297, 2926, 2918, 2189, 3160, 973, 1944, 2028,
                                 4299, 4299, 4299, 4299, 4299, 4299, 4299, 4299, 4299, 4299, 4299, 4299,
                                 4299, 4299, 4299, 4299, 4218, 2122, 1457, 626, 1443, 685, 3890, 4483,
                                 1761, 2224, 4942, 2799, 6177, 2699, 4670, 4830, 2582, 1763, 1516, 6048,
                                 3072, 3150, 5976, 4600, 2128, 2045, 1587, 64, 3650, 5915, 4742, 2699,
                                 134, 2125, 1278, 3888, 3646, 731, 784, 2004]]

    results = model.batch_infer(text_ids_list, prompt_speech_token_list)
    print(results)
