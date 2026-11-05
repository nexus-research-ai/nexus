import type { ChatCitation } from './api';

export type DemoEvidenceKey = 'eegDefense' | 'fragmentedPrivacy' | 'multiObjective' | 'communication';
export type DemoEvidence = ChatCitation & { key: DemoEvidenceKey; abstract: string };

export const demoEvidence: DemoEvidence[] = [
  {
    "key": "eegDefense",
    "source_id": "imported:zhibo_reputation-based_federated_learning_defense_to_mitigate_thre",
    "version": "1",
    "content_hash": "4ac0f3c74aa5edd2b972ba8080463971b23006ac30a91bb1b255a9a6c285abd5",
    "title": "Reputation-Based Federated Learning Defense to Mitigate Threats in EEG Signal Classification",
    "origin": "https://arxiv.org/pdf/2401.01896v1",
    "quote": "introduces a reputation-based mechanism to mitigate the influence of data poisoning attacks and identify compromised participants.",
    "abstract": "This paper presents a reputation-based threat mitigation framework that defends potential security threats in electroencephalogram (EEG) signal classification during model aggregation of Federated Learning. While EEG signal analysis has attracted attention because of the emergence of brain-computer interface (BCI) technology, it is difficult to create efficient learning models for EEG analysis because of the distributed nature of EEG data and related privacy and security concerns. To address these challenges, the proposed defending framework leverages the Federated Learning paradigm to preserve privacy by collaborative model training with localized data from dispersed sources and introduces a reputation-based mechanism to mitigate the influence of data poisoning attacks and identify compromised participants. To assess the efficiency of the proposed reputation-based federated learning defense framework, data poisoning attacks based on the risk level of training data derived by Explainable Artificial Intelligence (XAI) techniques are conducted on both publicly available EEG signal datasets and the self-established EEG signal dataset. Experimental results on the poisoned datasets show that the proposed defense methodology performs well in EEG signal classification while reducing the risks associated with security threats."
  },
  {
    "key": "fragmentedPrivacy",
    "source_id": "imported:najeeb_enhanced_security_and_privacy_via_fragmented_federated_learn",
    "version": "1",
    "content_hash": "04328758df15f4ca768e8dc45ce9aab6957fb9364d87eb24c05ff31dad2a5013",
    "title": "Enhanced Security and Privacy via Fragmented Federated Learning",
    "origin": "https://arxiv.org/pdf/2207.05978v2",
    "quote": "good updates sent by honest participants may reveal their private local information",
    "abstract": "In federated learning (FL), a set of participants share updates computed on their local data with an aggregator server that combines updates into a global model. However, reconciling accuracy with privacy and security is a challenge to FL. On the one hand, good updates sent by honest participants may reveal their private local information, whereas poisoned updates sent by malicious participants may compromise the model's availability and/or integrity. On the other hand, enhancing privacy via update distortion damages accuracy, whereas doing so via update aggregation damages security because it does not allow the server to filter out individual poisoned updates. To tackle the accuracy-privacy-security conflict, we propose {\\em fragmented federated learning} (FFL), in which participants randomly exchange and mix fragments of their updates before sending them to the server. To achieve privacy, we design a lightweight protocol that allows participants to privately exchange and mix encrypted fragments of their updates so that the server can neither obtain individual updates nor link them to their originators. To achieve security, we design a reputation-based defense tailored for FFL that builds trust in participants and their mixed updates based on the quality of the fragments they exchange and the mixed updates they send. Since the exchanged fragments' parameters keep their original coordinates and attackers can be neutralized, the server can correctly reconstruct a global model from the received mixed updates without accuracy loss. Experiments on four real data sets show that FFL can prevent semi-honest servers from mounting privacy attacks, can effectively counter poisoning attacks and can keep the accuracy of the global model."
  },
  {
    "key": "multiObjective",
    "source_id": "imported:haibo_federated_multi-objective_learning",
    "version": "1",
    "content_hash": "43786131504ca6a3c7275ffaaa36d7f33e9935fd45b523499669caf63ee42126",
    "title": "Federated Multi-Objective Learning",
    "origin": "https://arxiv.org/pdf/2310.09866v3",
    "quote": "Both algorithms allow local updates to significantly reduce communication costs",
    "abstract": "In recent years, multi-objective optimization (MOO) emerges as a foundational problem underpinning many multi-agent multi-task learning applications. However, existing algorithms in MOO literature remain limited to centralized learning settings, which do not satisfy the distributed nature and data privacy needs of such multi-agent multi-task learning applications. This motivates us to propose a new federated multi-objective learning (FMOL) framework with multiple clients distributively and collaboratively solving an MOO problem while keeping their training data private. Notably, our FMOL framework allows a different set of objective functions across different clients to support a wide range of applications, which advances and generalizes the MOO formulation to the federated learning paradigm for the first time. For this FMOL framework, we propose two new federated multi-objective optimization (FMOO) algorithms called federated multi-gradient descent averaging (FMGDA) and federated stochastic multi-gradient descent averaging (FSMGDA). Both algorithms allow local updates to significantly reduce communication costs, while achieving the {\\em same} convergence rates as those of their algorithmic counterparts in the single-objective federated learning. Our extensive experiments also corroborate the efficacy of our proposed FMOO algorithms."
  },
  {
    "key": "communication",
    "source_id": "imported:haibo_cfedavg_achieving_efficient_communication_and_fast_convergen",
    "version": "1",
    "content_hash": "64015daa713c9bb2ce2b559c47b40b4c7590f8086449c70e027714e0a71770fa",
    "title": "CFedAvg: Achieving Efficient Communication and Fast Convergence in Non-IID Federated Learning",
    "origin": "https://arxiv.org/pdf/2106.07155v1",
    "quote": "a large number of workers jointly learn a model without sharing their training data.",
    "abstract": "Federated learning (FL) is a prevailing distributed learning paradigm, where a large number of workers jointly learn a model without sharing their training data. However, high communication costs could arise in FL due to large-scale (deep) learning models and bandwidth-constrained connections. In this paper, we introduce a communication-efficient algorithmic framework called CFedAvg for FL with non-i.i.d. datasets, which works with general (biased or unbiased) SNR-constrained compressors. We analyze the convergence rate of CFedAvg for non-convex functions with constant and decaying learning rates. The CFedAvg algorithm can achieve an $\\mathcal{O}(1 / \\sqrt{mKT} + 1 / T)$ convergence rate with a constant learning rate, implying a linear speedup for convergence as the number of workers increases, where $K$ is the number of local steps, $T$ is the number of total communication rounds, and $m$ is the total worker number. This matches the convergence rate of distributed/federated learning without compression, thus achieving high communication efficiency while not sacrificing learning accuracy in FL. Furthermore, we extend CFedAvg to cases with heterogeneous local steps, which allows different workers to perform a different number of local steps to better adapt to their own circumstances. The interesting observation in general is that the noise/variance introduced by compressors does not affect the overall convergence rate order for non-i.i.d. FL. We verify the effectiveness of our CFedAvg algorithm on three datasets with two gradient compression schemes of different compression ratios."
  }
];

export const demoEvidenceByKey = Object.fromEntries(demoEvidence.map(item => [item.key, item])) as Record<DemoEvidenceKey, DemoEvidence>;
