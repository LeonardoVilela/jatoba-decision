# Attributions

JATOBÁ builds on the model and datasets below. Listing them does not imply that their authors endorse JATOBÁ. Each keeps its own license; see [`docs/final_weight_license_audit.md`](https://github.com/LeonardoVilela/jatoba-decision/blob/release/jatoba-v1.1/docs/final_weight_license_audit.md).

## Model

- **NorBERTo-base** (frozen encoder), Itaú Unibanco. [huggingface.co/Itau-Unibanco/NorBERTo-base](https://huggingface.co/Itau-Unibanco/NorBERTo-base) @ `db73446f`, CC BY-NC-SA 4.0.
  - Silva et al., "NorBERTo: A ModernBERT Model Trained for Portuguese with 331 Billion Tokens Corpus", PROPOR 2026. https://aclanthology.org/2026.propor-1.18/

## Training data

- **MASSIVE**, Amazon, CC BY 4.0.
  - FitzGerald et al., "MASSIVE: A 1M-Example Multilingual Natural Language Understanding Dataset with 51 Typologically-Diverse Languages", 2022. https://arxiv.org/abs/2204.08582
  - JATOBÁ used the pt-BR localization [Magurofg/massive-pt-br](https://huggingface.co/datasets/Magurofg/massive-pt-br) @ `907f905b`, CC BY 4.0.
- **ASSIN 2.** No license stated.
  - Real, Fonseca and Gonçalo Oliveira, "The ASSIN 2 Shared Task: A Quick Overview", PROPOR 2020. https://sites.google.com/view/assin2/
  - ASSIN 2 is based on SICK-BR (Real et al., PROPOR 2018), a translation of SICK (Marelli et al., LREC 2014; CC BY-NC-SA 3.0).
- **InferBR**, MIT.
  - Bencke, Pereira, Santos and Moreira, "InferBR: A Natural Language Inference Dataset in Portuguese", LREC-COLING 2024. https://aclanthology.org/2024.lrec-main.793 · https://github.com/lbencke/InferBR
- **ToLD-Br**, CC BY-SA 4.0.
  - Leite et al., "Toxic Language Detection in Social Media for Brazilian Portuguese: New Dataset and Multilingual Analysis", AACL-IJCNLP 2020. https://aclanthology.org/2020.aacl-main.91 · https://github.com/JAugusto97/ToLD-Br
- **HateBR**, CC BY-NC 4.0 (authors' repository).
  - Vargas, Carvalho, Góes, Pardo and Benevenuto, "HateBR: A Large Expert Annotated Corpus of Brazilian Instagram Comments for Offensive Language and Hate Speech Detection", LREC 2022. https://aclanthology.org/2022.lrec-1.777/ · https://github.com/franciellevargas/HateBR
- **BRIGHTER** (ptbr emotion intensities), CC BY 4.0.
  - Muhammad et al., "BRIGHTER: BRIdging the Gap in Human-Annotated Textual Emotion Recognition Datasets for 28 Languages", 2025. https://arxiv.org/abs/2502.11926
  - Muhammad et al., "SemEval-2025 Task 11: Bridging the Gap in Text-Based Emotion Detection", 2025. https://arxiv.org/abs/2503.07269
- **Community Alignment** (Portuguese first turn), Meta, CC BY 4.0.
  - Zhang et al., "Cultivating Pluralism In Algorithmic Monoculture: The Community Alignment Dataset", ICLR 2026. https://openreview.net/forum?id=4NtoAVqfhA

## Evaluation-only data

- **NormasTCU and JurisTCU** (Leandro Ribeiro), CC BY 4.0.
- **FaQuAD** (Sayama et al., 2019), https://github.com/liafacom/faquad.
