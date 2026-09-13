# Prospective MGSM study results

{
  "expected": 2300,
  "recorded": 2300,
  "statuses": {
    "ok": 1898,
    "generation_truncated": 19,
    "answer_unparseable": 383
  },
  "complete": true
}

## Cell outcomes

- Qwen en published brief: 54/250 scoreable, N=250; conditional 21.6%; bounds [21.6, 21.6]%.
- Qwen en published number_only: 28/100 scoreable, N=100; conditional 28.0%; bounds [28.0, 28.0]%.
- Qwen es archived brief: 11/50 scoreable, N=50; conditional 22.0%; bounds [22.0, 22.0]%.
- Qwen es published brief: 61/250 scoreable, N=250; conditional 24.4%; bounds [24.4, 24.4]%.
- Qwen es published number_only: 27/100 scoreable, N=100; conditional 27.0%; bounds [27.0, 27.0]%.
- Qwen zh archived brief: 5/50 scoreable, N=50; conditional 10.0%; bounds [10.0, 10.0]%.
- Qwen zh published brief: 31/247 scoreable, N=250; conditional 12.6%; bounds [12.4, 13.6]%.
- Qwen zh published number_only: 25/100 scoreable, N=100; conditional 25.0%; bounds [25.0, 25.0]%.
- Mistral en published brief: 76/139 scoreable, N=250; conditional 54.7%; bounds [30.4, 74.8]%.
- Mistral en published number_only: 8/65 scoreable, N=100; conditional 12.3%; bounds [8.0, 43.0]%.
- Mistral es archived brief: 5/20 scoreable, N=50; conditional 25.0%; bounds [10.0, 70.0]%.
- Mistral es published brief: 47/102 scoreable, N=250; conditional 46.1%; bounds [18.8, 78.0]%.
- Mistral es published number_only: 8/88 scoreable, N=100; conditional 9.1%; bounds [8.0, 20.0]%.
- Mistral zh archived brief: 9/35 scoreable, N=50; conditional 25.7%; bounds [18.0, 48.0]%.
- Mistral zh published brief: 92/203 scoreable, N=250; conditional 45.3%; bounds [36.8, 55.6]%.
- Mistral zh published number_only: 8/99 scoreable, N=100; conditional 8.1%; bounds [8.0, 9.0]%.

## Paired contrasts

- language, Qwen zh: n=247/250, B-A -9.3 pp, bootstrap [-14.6, -4.0]; bounds [-9.2, -8.0]; Holm p=0.0032963294383989705; equal-wrong 30.
- wording, Qwen zh: n=48/50, B-A -2.1 pp, bootstrap [-10.4, 6.2]; bounds [-2.0, 2.0]; Holm p=1; equal-wrong 8.
- language, Qwen es: n=250/250, B-A 2.8 pp, bootstrap [-2.4, 8.0]; bounds [2.8, 2.8]; Holm p=0.7425960689420208; equal-wrong 51.
- wording, Qwen es: n=50/50, B-A 2.0 pp, bootstrap [-6.0, 12.0]; bounds [2.0, 2.0]; Holm p=1; equal-wrong 16.
- format, Qwen en: n=100/100, B-A 2.0 pp, bootstrap [-3.0, 8.0]; bounds [2.0, 2.0]; Holm p=1; equal-wrong 33.
- format, Qwen zh: n=99/100, B-A 11.1 pp, bootstrap [3.0, 19.2]; bounds [10.0, 11.0]; Holm p=0.038177490234375; equal-wrong 19.
- format, Qwen es: n=100/100, B-A -1.0 pp, bootstrap [-8.0, 6.0]; bounds [-1.0, -1.0]; Holm p=1; equal-wrong 33.
- language, Mistral zh: n=112/250, B-A -12.5 pp, bootstrap [-23.2, -1.8]; bounds [-38.0, 25.2]; Holm p=0.10065731903887354; equal-wrong 4.
- wording, Mistral zh: n=27/50, B-A 18.5 pp, bootstrap [3.7, 33.3]; bounds [-14.0, 42.0]; Holm p=0.25; equal-wrong 1.
- language, Mistral es: n=62/250, B-A -4.8 pp, bootstrap [-19.4, 8.1]; bounds [-56.0, 47.6]; Holm p=0.7425960689420208; equal-wrong 4.
- wording, Mistral es: n=10/50, B-A 20.0 pp, bootstrap [-20.0, 60.0]; bounds [-50.0, 70.0]; Holm p=1; equal-wrong 1.
- format, Mistral en: n=41/100, B-A -43.9 pp, bootstrap [-61.0, -26.8]; bounds [-66.0, 6.0]; Holm p=0.0002002716064453125; equal-wrong 1.
- format, Mistral zh: n=78/100, B-A -32.1 pp, bootstrap [-43.6, -19.2]; bounds [-45.0, -23.0]; Holm p=2.7894973754882812e-05; equal-wrong 3.
- format, Mistral es: n=40/100, B-A -37.5 pp, bootstrap [-55.0, -20.0]; bounds [-71.0, -1.0]; Holm p=0.0029144287109375; equal-wrong 2.
