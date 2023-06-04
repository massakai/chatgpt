# chatgpt

## セットアップ

```bash
$ brew install portaudio
```

Poetryをインストールする。

```bash
$ pip install poetry
```

依存ライブラリをインストールする。

```bash
$ poetry install
```

## 実行方法

Google CloudでSpeech-to-Text API, Text-to-Speech APIを利用するため、サービスアカウントの認証情報が必要になります。
また、OpenAIのAPIを利用するためのキーも必要になります。

```bash
$ export OPENAI_API_KEY=sk-JEFZq...
$ export GOOGLE_APPLICATION_CREDENTIALS=/Users/massakai/Downloads/massakai-project-sandbox-7c6d1538c588.json

$ python -m chatgpt.main
user: こんばんは
assistant: 、私はAIアシスタントです。何かお力になれることがあれば教えてください。
user: マリオカート8デラックスについて教えてください
assistant: マリオカート8デラックスは、任天堂が発売したNintendo Switch用のレースゲームです。以下が特徴的な内容です。

- 最大8人までのオンライン対戦が可能です。
- レーストラックは、過去のシリーズからの人気のある要素を含む、全48トラックが収録されています。
- 新しい要素として、クッパJr.、キノピオ、ブーメランメットなどの新しいキャラクターや、マルチプレイヤーや一人用のアイテムバトルモードが収録されています。
- ジャンプループ、トランポリン、滑走路など、地形的な要素がレースに含まれています。
- Joy-Conを使ったモーション操作対応や、HD振動に対応したリアルな振動を感じることができます。

以上が、マリオカート8デラックスの基本的な情報になります。
user: ありがとう
assistant: どういたしまして。何か質問があれば気軽にお知らせください。
user: 終わり
Exiting..

```
