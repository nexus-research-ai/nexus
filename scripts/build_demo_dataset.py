#!/usr/bin/env python3
"""Builds high-fidelity 30-paper dataset with Meta API parsing structures,

grounded claims, SAM 3.1 figure bounding boxes, and realistic American researcher profiles.
"""

import os
import json

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(REPO_ROOT, "data")
os.makedirs(DATA_DIR, exist_ok=True)

# 12 American researcher & student profiles
PROFILES = [
    {
        "id": "user-aria",
        "name": "Aria Malik",
        "initials": "AM",
        "avatar_url": "/avatars/aria_malik.jpg",
        "degree": "MSCS Candidate",
        "title": "Graduate Researcher",
        "dept": "EECS · Helen Wills Neuroscience",
        "institution": "UC Berkeley",
        "bio": "Representation learning, federated adaptation layers, and non-invasive EEG decoding. Building privacy-preserving models for neural prosthetics.",
        "color": "gold",
        "role": "Lead Author / Pod Lead",
        "offers": ["Optimal transport", "Adapter weights", "PyTorch codebase", "Differential privacy auditing"],
        "needs": ["Longitudinal EEG", "Clinical sleep cohorts", "Mobile 128-channel EEG", "Compute grant"],
        "stage": "PROTOTYPE",
        "degree_label": "MSCS",
        "active_grant": "NSF Smart & Connected Health ($1,200,000)",
        "readiness_score": 72,
        "certificates": ["NX-8821", "NX-8822"]
    },
    {
        "id": "user-jon",
        "name": "Jon Lee",
        "initials": "JL",
        "avatar_url": "/avatars/jon_lee.jpg",
        "degree": "PhD Candidate",
        "title": "Systems & Privacy Researcher",
        "dept": "Computer Science & Engineering",
        "institution": "UC Berkeley",
        "bio": "Distributed optimization, split learning, and zero-knowledge model partitioning under extreme bandwidth constraints.",
        "color": "blue",
        "role": "Pod Member · Systems",
        "offers": ["Split learning kernels", "CUDA parameter clipping", "Zero-leakage gradients"],
        "needs": ["Multi-site sensor telemetry", "FPGA testbed", "Edge benchmark suites"],
        "stage": "ACTIVE",
        "degree_label": "PhD",
        "active_grant": "DARPA Young Faculty Award ($500,000)",
        "readiness_score": 85,
        "certificates": ["NX-4109"]
    },
    {
        "id": "user-maya",
        "name": "Maya Rodriguez",
        "initials": "MR",
        "avatar_url": "/avatars/maya_rodriguez.jpg",
        "degree": "Postdoctoral Fellow",
        "title": "Autonomous Systems Engineer",
        "dept": "Robotics & Autonomous Systems",
        "institution": "UC Berkeley",
        "bio": "Soft conductive elastomers, continuous micro-strain monitoring, and real-time motion artifact filtering for aerial robots.",
        "color": "violet",
        "role": "Pod Member · Hardware",
        "offers": ["Cleanroom fabrication", "Micro-strain sensor hardware", "Mechanical load testing"],
        "needs": ["Real-time drift modeling", "Embedded DSP firmware", "Field trial partner"],
        "stage": "DISCOVERY",
        "degree_label": "Postdoc",
        "active_grant": "NSF CAREER ($600,000)",
        "readiness_score": 68,
        "certificates": ["NX-5531"]
    },
    {
        "id": "user-rao",
        "name": "Prof. Sarah Rao",
        "initials": "SR",
        "avatar_url": "/avatars/sarah_rao.jpg",
        "degree": "Associate Professor",
        "title": "Principal Investigator & Lab Director",
        "dept": "EECS & Computational Precision Health",
        "institution": "UC Berkeley",
        "bio": "Differential privacy bounds, federated healthcare fleets, and provable algorithmic fairness in non-invasive neural decoders.",
        "color": "teal",
        "role": "Faculty Advisor / Co-PI",
        "offers": ["DP formal verification", "Multi-site IRB navigation", "Nature MI pre-print access"],
        "needs": ["Clinical hospital partners", "Pediatric neuro-telemetry", "DOE supercomputing allocation"],
        "stage": "PRE-PRINT",
        "degree_label": "Faculty",
        "active_grant": "NSF Smart and Connected Health ($1,200,000)",
        "readiness_score": 94,
        "certificates": ["NX-1002", "NX-1003"]
    },
    {
        "id": "user-jordan",
        "name": "Jordan Hayes",
        "initials": "JH",
        "avatar_url": "/avatars/jordan_hayes.jpg",
        "degree": "PhD Candidate",
        "title": "Cognitive Neuroscientist",
        "dept": "Helen Wills Neuroscience Institute",
        "institution": "UC Berkeley",
        "bio": "High-density mobile neurotelemetry, 128-channel dry electrode recordings, and auditory cortex event-related potential decoding.",
        "color": "gold",
        "role": "Collaborator · Mutual Match",
        "offers": ["128-channel mobile EEG lab", "Event-related potential pipelines", "Clinical cohort access"],
        "needs": ["Federated representation learning", "Cross-subject latent alignment", "Privacy audit tools"],
        "stage": "PROTOTYPE",
        "degree_label": "PhD",
        "active_grant": "NIH R21 Exploratory Research ($275,000)",
        "readiness_score": 91,
        "certificates": ["NX-6218"]
    },
    {
        "id": "user-marcus",
        "name": "Marcus Vance",
        "initials": "MV",
        "avatar_url": "/avatars/marcus_vance.jpg",
        "degree": "PhD Researcher",
        "title": "Neuroengineering Specialist",
        "dept": "Bioengineering & Neurotechnology",
        "institution": "UC Berkeley",
        "bio": "Synchronized multimodal telemetry for freely moving subjects, sub-millivolt surface biopotentials, and wireless optogenetic sync.",
        "color": "orange",
        "role": "Campus Researcher",
        "offers": ["Optical hardware sync", "Sub-millivolt amplifiers", "Benchmarking telemetry"],
        "needs": ["Cross-cohort validation", "Wireless telemetry rig", "Biopotential filtering"],
        "stage": "PROTOTYPE",
        "degree_label": "PhD",
        "active_grant": "DARPA Young Faculty Award ($500,000)",
        "readiness_score": 77,
        "certificates": ["NX-7714"]
    },
    {
        "id": "user-emily",
        "name": "Emily Chen",
        "initials": "EC",
        "avatar_url": "/avatars/emily_chen.jpg",
        "degree": "PhD Candidate",
        "title": "Computer Vision & Multimodal AI",
        "dept": "EECS · Berkeley AI Research (BAIR)",
        "institution": "UC Berkeley",
        "bio": "Pixel-to-proof visual grounding, scientific figure segmentation using Meta SAM 3.1, and diagrammatic reasoning over neural charts.",
        "color": "violet",
        "role": "Vision Specialist",
        "offers": ["SAM 3.1 fine-tuning", "Scientific diagram parsing", "Multimodal figure grounding"],
        "needs": ["Microscopy datasets", "Neural spectrograms", "Grant figures"],
        "stage": "PRE-PRINT",
        "degree_label": "PhD",
        "active_grant": "NSF CAREER ($600,000)",
        "readiness_score": 88,
        "certificates": ["NX-3390"]
    },
    {
        "id": "user-david",
        "name": "David Miller",
        "initials": "DM",
        "avatar_url": "/avatars/david_miller.jpg",
        "degree": "Staff Research Scientist",
        "title": "Bioinformatics & Genomics",
        "dept": "Computational Biology & Genomics",
        "institution": "UC Berkeley",
        "bio": "Single-cell transcriptome alignment, differential gene expression, and federated patient cohort clustering.",
        "color": "blue",
        "role": "Bioinformatics Scientist",
        "offers": ["Single-cell pipelines", "Genomic manifold alignment", "Nextflow workflows"],
        "needs": ["Differential privacy bounds", "GPU clustering clusters", "Multi-institution consortium"],
        "stage": "ACTIVE",
        "degree_label": "Staff Scientist",
        "active_grant": "NIH R01 Research Project ($1,850,000)",
        "readiness_score": 82,
        "certificates": ["NX-2045"]
    },
    {
        "id": "user-rachel",
        "name": "Rachel Adams",
        "initials": "RA",
        "avatar_url": "/avatars/rachel_adams.jpg",
        "degree": "MS Candidate",
        "title": "Aerospace & Embedded Systems",
        "dept": "Mechanical Engineering",
        "institution": "UC Berkeley",
        "bio": "Ultra-lightweight sensor packages for UAVs, structural vibration monitoring, and micro-strain telemetry.",
        "color": "teal",
        "role": "Mechanical Engineer",
        "offers": ["UAV airframe design", "Composite materials testing", "CAD/FEA simulations"],
        "needs": ["Wireless telemetry sync", "Embedded ML inference", "Field deployment sites"],
        "stage": "DISCOVERY",
        "degree_label": "MS",
        "active_grant": "NASA Space Technology Grant ($175,000)",
        "readiness_score": 64,
        "certificates": ["NX-4912"]
    },
    {
        "id": "user-alex",
        "name": "Alex Rivera",
        "initials": "AR",
        "avatar_url": "/avatars/alex_rivera.jpg",
        "degree": "Graduate Researcher",
        "title": "Health Informatics Specialist",
        "dept": "School of Public Health & EECS",
        "institution": "UC Berkeley",
        "bio": "Differential privacy bounds in longitudinal digital health, clinical trials data sharing, and ethical AI in biometrics.",
        "color": "gold",
        "role": "Informatics Researcher",
        "offers": ["DP audit scripts", "Synthetic cohort generators", "Ethical AI benchmarks"],
        "needs": ["Real EEG telemetry", "Secure enclave access", "Clinical collaborators"],
        "stage": "ACTIVE",
        "degree_label": "PhD",
        "active_grant": "NIH R21 Exploratory Research ($275,000)",
        "readiness_score": 79,
        "certificates": ["NX-9104"]
    },
    {
        "id": "user-tyler",
        "name": "Tyler Scott",
        "initials": "TS",
        "avatar_url": "/avatars/tyler_scott.jpg",
        "degree": "Postdoctoral Fellow",
        "title": "Quantum & Hardware Systems",
        "dept": "Electrical Engineering & Computer Sciences",
        "institution": "UC Berkeley",
        "bio": "Sub-threshold neuromorphic circuits, cryogenic CMOS readout for biopotentials, and on-chip cryptographic accelerators.",
        "color": "orange",
        "role": "Hardware Postdoc",
        "offers": ["ASIC design tape-outs", "FPGA hardware acceleration", "Cryogenic test setups"],
        "needs": ["Spike-based EEG data", "Low-power algorithm partners", "Clinical verification"],
        "stage": "PROTOTYPE",
        "degree_label": "Postdoc",
        "active_grant": "DARPA Young Faculty Award ($500,000)",
        "readiness_score": 86,
        "certificates": ["NX-6721"]
    },
    {
        "id": "user-elena",
        "name": "Prof. Elena Vasquez",
        "initials": "EV",
        "avatar_url": "/avatars/elena_vasquez.jpg",
        "degree": "Full Professor",
        "title": "Director, Neuroengineering Center",
        "dept": "Bioengineering & Helen Wills Neuroscience",
        "institution": "UC Berkeley",
        "bio": "Non-invasive neural interfaces, cortical plasticity, closed-loop neural stimulation, and cross-disciplinary grant mentorship.",
        "color": "violet",
        "role": "Department Director / Senior PI",
        "offers": ["Center lab space", "High-density primate/human EEG suites", "Institutional support"],
        "needs": ["Federated decoding methods", "Scalable cloud inference", "Junior Co-PIs"],
        "stage": "ACTIVE",
        "degree_label": "Faculty",
        "active_grant": "NSF Smart and Connected Health ($1,200,000)",
        "readiness_score": 98,
        "certificates": ["NX-1001"]
    }
]

# 30 deeply parsed papers grounded in peer-reviewed scientific domains
PAPERS = [
    {
        "id": "paper-1",
        "title": "Federated Foundation Models for Privacy-Preserving Neural Decoding",
        "authors": "Zhang, W., Chen, S., Lee, J., Rao, S.",
        "journal": "Nature Machine Intelligence",
        "year": 2024,
        "doi": "10.1038/s42256-024-00812-x",
        "score": 96,
        "verdict": "Supports",
        "person": "MR",
        "color": "blue",
        "department": "EECS & Computational Precision Health",
        "abstract": "We present the first foundation model architecture for non-invasive neural decoding trained across decentralized clinical fleets using differential privacy. By decoupling subject-specific adapter heads from a shared latent manifold, our method achieves 94.2% within-subject retention across 5 held-out cohorts without pooling raw biopotentials.",
        "claims": [
            {
                "claim_id": "c1-1",
                "text": "Within-subject latent retention is preserved at 94.2% across 5 held-out cohorts under bounded DP noise (epsilon = 0.5).",
                "grounding_source": "Figure 4b, page 8",
                "bbox": [120, 85, 480, 360],
                "confidence": 0.98,
                "status": "VERIFIED"
            },
            {
                "claim_id": "c1-2",
                "text": "Calibration time is reduced by 61% compared to cold-start transfer when parameter clipping bounds are enforced at communication boundaries.",
                "grounding_source": "Table 2, page 6",
                "bbox": [95, 210, 510, 390],
                "confidence": 0.96,
                "status": "VERIFIED"
            }
        ],
        "figure_grounding": {
            "figure_id": "fig4b",
            "title": "Cross-Site Latent Calibration and Parameter Retention",
            "file": "/figures/figure_4b_neural_alignment.png",
            "caption": "Within-subject retention across 5 cohorts comparing Baseline vs Federated Optimal Transport."
        },
        "target_grant": "NSF Smart & Connected Health"
    },
    {
        "id": "paper-2",
        "title": "Cross-Subject EEG Alignment via Optimal Transport on Riemannian Manifolds",
        "authors": "Li, Z., Verma, A., Malik, A., Hayes, J.",
        "journal": "NeurIPS 2024",
        "year": 2024,
        "doi": "10.48550/arXiv.2405.11928",
        "score": 91,
        "verdict": "Methodology",
        "person": "JL",
        "color": "violet",
        "department": "Helen Wills Neuroscience Institute",
        "abstract": "Inter-subject variability poses a severe obstacle for brain-computer interfaces. We formulate cross-subject manifold alignment as an entropic regularized optimal transport problem on Riemannian covariance manifolds, guaranteeing geometric consistency while minimizing distributional Wasserstein distance.",
        "claims": [
            {
                "claim_id": "c2-1",
                "text": "Entropic optimal transport reduces Wasserstein distance between subject manifolds by 43.8% in less than 15 iterations.",
                "grounding_source": "Proposition 3.2, page 4",
                "bbox": [80, 150, 460, 280],
                "confidence": 0.94,
                "status": "VERIFIED"
            }
        ],
        "target_grant": "NIH R21 Neurotechnology"
    },
    {
        "id": "paper-3",
        "title": "The Privacy Cost of Brain–Computer Interfaces: Membership Inference Risks in Shared Latents",
        "authors": "Rao, S., Adams, R., Shokri, R.",
        "journal": "ACM Conference on Fairness, Accountability, and Transparency (FAccT)",
        "year": 2023,
        "doi": "10.1145/3593013.3594002",
        "score": 88,
        "verdict": "Contradicts",
        "person": "AM",
        "color": "gold",
        "department": "EECS",
        "abstract": "We demonstrate that naive federated learning of neural decoding adapters leaks private patient identity through membership inference attacks with up to 78.4% precision if gradient obfuscation is not mathematically bounded by Renyi differential privacy.",
        "claims": [
            {
                "claim_id": "c3-1",
                "text": "Unclipped gradient exchange allows an active adversary to reconstruct individual EEG evoked responses with 78.4% precision.",
                "grounding_source": "Section 4.1, Theorem 1, page 7",
                "bbox": [110, 310, 490, 440],
                "confidence": 0.95,
                "status": "CONTRADICTS_NAIVE_FEDERATION"
            }
        ],
        "target_grant": "DARPA Young Faculty Award"
    },
    {
        "id": "paper-4",
        "title": "HOSL: Hybrid-Order Split Learning for Memory-Constrained Edge Training",
        "authors": "Lnu, A., Li, Z., Liang, D., Lee, J., Yang, H.",
        "journal": "IEEE Transactions on Mobile Computing",
        "year": 2024,
        "doi": "10.1109/TMC.2024.3391820",
        "score": 93,
        "verdict": "Supports",
        "person": "JL",
        "color": "blue",
        "department": "Computer Science & Systems",
        "abstract": "Split learning partitions neural computation across edge devices and cloud servers. By integrating zeroth-order gradient estimation at the client with first-order backpropagation at the server, HOSL reduces client GPU memory overhead by 3.7x with less than 1.2% accuracy degradation.",
        "claims": [
            {
                "claim_id": "c4-1",
                "text": "Client-side GPU memory consumption drops by 3.7x compared to standard first-order backpropagation.",
                "grounding_source": "Figure 5, page 9",
                "bbox": [100, 120, 500, 340],
                "confidence": 0.97,
                "status": "VERIFIED"
            }
        ],
        "target_grant": "DOE Advanced Scientific Computing Research"
    },
    {
        "id": "paper-5",
        "title": "Low-Overhead Soft Conductive Elastomers for Continuous Micro-Strain Telemetry",
        "authors": "Rodriguez, M., Adams, R., Thorne, M.",
        "journal": "Advanced Functional Materials",
        "year": 2024,
        "doi": "10.1002/adfm.202314502",
        "score": 90,
        "verdict": "Supports",
        "person": "MR",
        "color": "violet",
        "department": "Robotics & Autonomous Systems",
        "abstract": "We fabricate multi-material carbon nanotube elastomers exhibiting linear gauge factors over 150% strain with negligible hysteresis. Real-time drift filtering embedded in low-power firmware yields sub-millivolt telemetry suitable for aerial wing monitoring.",
        "claims": [
            {
                "claim_id": "c5-1",
                "text": "Multi-material conductive elastomer maintains linearity under 100,000 cyclic strain loadings with drift under 0.8%.",
                "grounding_source": "Figure 3c, page 5",
                "bbox": [130, 90, 470, 310],
                "confidence": 0.96,
                "status": "VERIFIED"
            }
        ],
        "target_grant": "NSF CAREER"
    },
    {
        "id": "paper-6",
        "title": "Differentially Private Parameter Aggregation in Decentralized Healthcare Fleets",
        "authors": "Kairouz, P., McMahan, H. B., Rao, S., Rivera, A.",
        "journal": "Nature Digital Medicine",
        "year": 2024,
        "doi": "10.1038/s41746-024-01052-1",
        "score": 95,
        "verdict": "Supports",
        "person": "MR",
        "color": "blue",
        "department": "Computational Precision Health",
        "abstract": "Healthcare institutions face stringent regulatory boundaries preventing centralized clinical records pooling. We establish formal differential privacy guarantees for decentralized parameter aggregation using moment accountants across 14 hospital sites.",
        "claims": [
            {
                "claim_id": "c6-1",
                "text": "Formal privacy parameter (epsilon = 1.2, delta = 1e-5) is preserved across 50 federated rounds without patient re-identification.",
                "grounding_source": "Theorem 2, page 6",
                "bbox": [90, 180, 510, 350],
                "confidence": 0.99,
                "status": "VERIFIED"
            }
        ],
        "target_grant": "NSF Smart and Connected Health"
    },
    {
        "id": "paper-7",
        "title": "Riemannian Geometries for Manifold Alignment of Evoked Surface Biopotentials",
        "authors": "Barachant, A., Bonnet, S., Malik, A., Vasquez, E.",
        "journal": "IEEE Transactions on Biomedical Engineering",
        "year": 2023,
        "doi": "10.1109/TBME.2023.3289012",
        "score": 89,
        "verdict": "Methodology",
        "person": "JL",
        "color": "violet",
        "department": "Bioengineering & Helen Wills Neuroscience",
        "abstract": "Covariance matrices of multi-channel biopotentials lie on a differentiable Riemannian manifold of symmetric positive-definite matrices. We introduce affine-invariant distance metrics that project heterogeneous sensor montages into a unified tangent space.",
        "claims": [
            {
                "claim_id": "c7-1",
                "text": "Affine-invariant Riemannian projection boosts cross-subject classification accuracy by 14.6% over Euclidean baseline.",
                "grounding_source": "Table 1, page 4",
                "bbox": [100, 220, 480, 370],
                "confidence": 0.93,
                "status": "VERIFIED"
            }
        ],
        "target_grant": "NIH R21 Neurotechnology"
    },
    {
        "id": "paper-8",
        "title": "Membership Inference Vulnerabilities in Federated Latent Embeddings",
        "authors": "Shokri, R., Carlini, N., Rivera, A.",
        "journal": "IEEE Symposium on Security and Privacy (S&P)",
        "year": 2024,
        "doi": "10.1109/SP.2024.1029811",
        "score": 84,
        "verdict": "Contradicts",
        "person": "AM",
        "color": "gold",
        "department": "EECS",
        "abstract": "We reveal that sharing lower-layer adapter embeddings in federated foundation models without noise perturbation allows an adversary to infer whether a patient was part of the training cohort with 86.1% AUC.",
        "claims": [
            {
                "claim_id": "c8-1",
                "text": "Unperturbed adapter weights exhibit shadow-model membership inference AUC of 0.861.",
                "grounding_source": "Figure 6a, page 11",
                "bbox": [115, 140, 495, 380],
                "confidence": 0.94,
                "status": "CONTRADICTS_NAIVE_SHARING"
            }
        ],
        "target_grant": "DARPA Young Faculty Award"
    },
    {
        "id": "paper-9",
        "title": "Synchronized Multimodal Telemetry for Freely Moving Subjects",
        "authors": "Vance, M., Scott, T., Vasquez, E.",
        "journal": "Nature Neuroscience Methods",
        "year": 2024,
        "doi": "10.1038/s41593-024-01618-9",
        "score": 92,
        "verdict": "Supports",
        "person": "MV",
        "color": "blue",
        "department": "Bioengineering & Neurotechnology",
        "abstract": "We construct a sub-milligram wireless telemetry package coupling 64-channel sub-millivolt surface biopotentials with 240 Hz optical motion capture, synchronized via precision time protocol with sub-microsecond jitter.",
        "claims": [
            {
                "claim_id": "c9-1",
                "text": "Synchronization jitter between optical tracking and biopotential streams is strictly below 0.42 microseconds.",
                "grounding_source": "Figure 2, page 3",
                "bbox": [85, 110, 475, 320],
                "confidence": 0.97,
                "status": "VERIFIED"
            }
        ],
        "target_grant": "DARPA Young Faculty Award"
    },
    {
        "id": "paper-10",
        "title": "Pixel-to-Proof: Grounding Scientific Claims in Multimodal Figures via SAM 3.1",
        "authors": "Chen, E., Malik, A., Thorne, M.",
        "journal": "CVPR 2024",
        "year": 2024,
        "doi": "10.48550/arXiv.2404.09812",
        "score": 94,
        "verdict": "Supports",
        "person": "EC",
        "color": "blue",
        "department": "EECS · BAIR",
        "abstract": "We leverage Meta SAM 3.1 zero-shot segmentation prompts to isolate exact figure sub-panels, error bars, and axis labels cited in academic text, generating verifiable visual bounding box grounding certificates.",
        "claims": [
            {
                "claim_id": "c10-1",
                "text": "SAM 3.1 zero-shot prompt segmentation achieves 96.8% precision in delineating multi-panel scientific charts.",
                "grounding_source": "Figure 4, page 7",
                "bbox": [105, 95, 490, 335],
                "confidence": 0.98,
                "status": "VERIFIED"
            }
        ],
        "target_grant": "NSF CAREER"
    },
    {
        "id": "paper-11",
        "title": "Scalable Manifold Alignment for Multi-Omics Single-Cell Cohorts",
        "authors": "Miller, D., Chen, S., Rao, S.",
        "journal": "Genome Biology",
        "year": 2024,
        "doi": "10.1186/s13059-024-03211-4",
        "score": 91,
        "verdict": "Supports",
        "person": "DM",
        "color": "teal",
        "department": "Computational Biology & Genomics",
        "abstract": "Aligning single-cell RNA-seq and ATAC-seq across decentralized clinical labs requires preserving cell trajectory topology while avoiding batch integration distortion. We develop an optimal transport solver that scales to 10M cells.",
        "claims": [
            {
                "claim_id": "c11-1",
                "text": "Single-cell topological manifold alignment scales to 10 million cells with linear memory complexity O(N).",
                "grounding_source": "Theorem 1, page 5",
                "bbox": [90, 160, 480, 310],
                "confidence": 0.95,
                "status": "VERIFIED"
            }
        ],
        "target_grant": "NIH R01 Research Project"
    },
    {
        "id": "paper-12",
        "title": "Cryogenic CMOS Readout Circuits for Ultra-Low Noise Neural Recording",
        "authors": "Scott, T., Vance, M., Vasquez, E.",
        "journal": "IEEE Journal of Solid-State Circuits",
        "year": 2024,
        "doi": "10.1109/JSSC.2024.3361922",
        "score": 88,
        "verdict": "Methodology",
        "person": "TS",
        "color": "orange",
        "department": "EECS",
        "abstract": "We fabricate a 0.5V sub-threshold analog front-end delivering 1.8 uVrms input-referred noise across 10 kHz bandwidth for direct integration with multi-electrode arrays.",
        "claims": [
            {
                "claim_id": "c12-1",
                "text": "Input-referred noise is suppressed to 1.8 uVrms with total power consumption under 32 uW per channel.",
                "grounding_source": "Figure 8b, page 9",
                "bbox": [110, 130, 490, 340],
                "confidence": 0.94,
                "status": "VERIFIED"
            }
        ],
        "target_grant": "DARPA Young Faculty Award"
    },
    {
        "id": "paper-13",
        "title": "Entropic Regularization Bounds for Fast Distributed Sinkhorn Iterations",
        "authors": "Verma, A., Li, Z., Malik, A.",
        "journal": "SIAM Journal on Optimization",
        "year": 2023,
        "doi": "10.1137/22M1490212",
        "score": 87,
        "verdict": "Methodology",
        "person": "AM",
        "color": "violet",
        "department": "EECS",
        "abstract": "Sinkhorn iterations provide efficient computation of optimal transport plans. We establish tight non-asymptotic convergence bounds for distributed asynchronous Sinkhorn updates across peer-to-peer compute nodes.",
        "claims": [
            {
                "claim_id": "c13-1",
                "text": "Asynchronous distributed Sinkhorn converges in O(1/eps^2) communication rounds under 20% packet loss.",
                "grounding_source": "Theorem 4, page 12",
                "bbox": [75, 175, 465, 330],
                "confidence": 0.92,
                "status": "VERIFIED"
            }
        ],
        "target_grant": "DOE Advanced Scientific Computing Research"
    },
    {
        "id": "paper-14",
        "title": "Drift-Resistant Strain Gauges via Carbon Nanotube Percolation Networks",
        "authors": "Adams, R., Rodriguez, M., Thorne, M.",
        "journal": "ACS Nano",
        "year": 2024,
        "doi": "10.1021/acsnano.4c01923",
        "score": 90,
        "verdict": "Supports",
        "person": "MR",
        "color": "teal",
        "department": "Mechanical Engineering",
        "abstract": "Percolation networks of aligned carbon nanotubes embedded in PDMS substrates suppress temporal resistance drift by 82% compared to random networks under high humidity and temperature swings.",
        "claims": [
            {
                "claim_id": "c14-1",
                "text": "Aligned percolation morphology suppresses thermal baseline drift to less than 0.05% per degree Celsius.",
                "grounding_source": "Figure 4, page 6",
                "bbox": [100, 115, 485, 325],
                "confidence": 0.96,
                "status": "VERIFIED"
            }
        ],
        "target_grant": "NASA Space Technology Grant"
    },
    {
        "id": "paper-15",
        "title": "Verifiable Machine Learning for Biomedical Signal Decoding",
        "authors": "Rivera, A., Rao, S., Lee, J.",
        "journal": "Journal of Machine Learning Research (JMLR)",
        "year": 2024,
        "doi": "10.5555/3648699.3648712",
        "score": 93,
        "verdict": "Supports",
        "person": "JL",
        "color": "blue",
        "department": "EECS & Public Health",
        "abstract": "We construct cryptographic zero-knowledge proofs certifying that a neural decoding pipeline adhered to differential privacy noise budgets and training hyper-parameters without revealing patient data.",
        "claims": [
            {
                "claim_id": "c15-1",
                "text": "Zero-knowledge proof verification of differential privacy bounds requires less than 45 ms on standard x86 CPU.",
                "grounding_source": "Table 3, page 8",
                "bbox": [90, 200, 500, 360],
                "confidence": 0.98,
                "status": "VERIFIED"
            }
        ],
        "target_grant": "NSF Smart and Connected Health"
    },
    {
        "id": "paper-16",
        "title": "Cortical Source Localization via Sparse Bayesian Learning over Non-Invasive Montages",
        "authors": "Hayes, J., Vasquez, E., Verma, A.",
        "journal": "NeuroImage",
        "year": 2024,
        "doi": "10.1016/j.neuroimage.2024.120512",
        "score": 89,
        "verdict": "Methodology",
        "person": "JH",
        "color": "gold",
        "department": "Helen Wills Neuroscience Institute",
        "abstract": "Solving the inverse EEG problem requires estimating dipole current densities within 3D cortical meshes. We demonstrate sparse Bayesian learning that reconstructs deep subcortical activations from 128-channel scalp recordings.",
        "claims": [
            {
                "claim_id": "c16-1",
                "text": "Localization dipole error in motor cortex activations is bounded under 3.4 mm across 18 healthy subjects.",
                "grounding_source": "Figure 5b, page 8",
                "bbox": [105, 100, 490, 315],
                "confidence": 0.94,
                "status": "VERIFIED"
            }
        ],
        "target_grant": "NIH R21 Neurotechnology"
    },
    {
        "id": "paper-17",
        "title": "Adaptive Zeroth-Order Perturbation for Edge Device Parameter Offloading",
        "authors": "Li, Z., Lnu, A., Lee, J.",
        "journal": "ICLR 2024",
        "year": 2024,
        "doi": "10.48550/arXiv.2402.08912",
        "score": 92,
        "verdict": "Supports",
        "person": "JL",
        "color": "blue",
        "department": "EECS",
        "abstract": "Zeroth-order optimization avoids backpropagation by sampling two forward queries with random gaussian perturbations. We introduce an adaptive covariance scheduler that accelerates edge convergence by 2.4x.",
        "claims": [
            {
                "claim_id": "c17-1",
                "text": "Adaptive perturbation covariance accelerates zeroth-order gradient convergence by 2.4x over standard SPSA.",
                "grounding_source": "Theorem 2, page 5",
                "bbox": [85, 145, 475, 305],
                "confidence": 0.95,
                "status": "VERIFIED"
            }
        ],
        "target_grant": "DOE Advanced Scientific Computing Research"
    },
    {
        "id": "paper-18",
        "title": "Automated Review Rubric Simulation via Meta Muse Reasoning",
        "authors": "Malik, A., Rao, S., Chen, E.",
        "journal": "Artificial Intelligence Review",
        "year": 2024,
        "doi": "10.1007/s10462-024-10819-2",
        "score": 96,
        "verdict": "Supports",
        "person": "AM",
        "color": "violet",
        "department": "EECS",
        "abstract": "Federal grant solicitations (NSF, NIH) grade proposals on strict rubric criteria including Intellectual Merit, Broader Impacts, and Technical Feasibility. We evaluate frontier reasoning models for automated pre-flight review simulation.",
        "claims": [
            {
                "claim_id": "c18-1",
                "text": "Pre-flight reviewer rubric simulation achieves 0.91 correlation with actual NSF panel scoring decisions.",
                "grounding_source": "Figure 3, page 6",
                "bbox": [110, 105, 495, 320],
                "confidence": 0.97,
                "status": "VERIFIED"
            }
        ],
        "target_grant": "NSF Smart and Connected Health"
    },
    {
        "id": "paper-19",
        "title": "Bio-Inspired Spatial Attention for Multi-Channel Electrophysiology",
        "authors": "Chen, S., Vance, M., Malik, A.",
        "journal": "IEEE Transactions on Neural Systems and Rehabilitation Engineering",
        "year": 2023,
        "doi": "10.1109/TNSRE.2023.3312019",
        "score": 88,
        "verdict": "Methodology",
        "person": "MV",
        "color": "blue",
        "department": "Bioengineering",
        "abstract": "Cortical electrical activity spreads across skull volume conductors. We design a geometrically constrained spatial attention mechanism that learns topographic electrode weights matching forward volume conductor models.",
        "claims": [
            {
                "claim_id": "c19-1",
                "text": "Spatial attention assigns 88.4% of total weight to electrodes within 2.5 cm of active cortical dipole coordinates.",
                "grounding_source": "Figure 6, page 9",
                "bbox": [95, 130, 485, 345],
                "confidence": 0.93,
                "status": "VERIFIED"
            }
        ],
        "target_grant": "NIH R21 Neurotechnology"
    },
    {
        "id": "paper-20",
        "title": "Provably Secure Parameter Exchange in Federated Research Consortia",
        "authors": "Rivera, A., Scott, T., Rao, S.",
        "journal": "ACM Transactions on Privacy and Security (TOPS)",
        "year": 2024,
        "doi": "10.1145/3651201",
        "score": 94,
        "verdict": "Supports",
        "person": "AR",
        "color": "teal",
        "department": "EECS & Public Health",
        "abstract": "We specify an information-flow control protocol for bilateral research matchmaking. Encrypted private vaults release zero-knowledge teasers and enforce mutual opt-in consent before disclosing researcher identities.",
        "claims": [
            {
                "claim_id": "c20-1",
                "text": "Bilateral double opt-in protocol guarantees zero leakage of private proposal hypotheses prior to mutual consent.",
                "grounding_source": "Theorem 1, page 7",
                "bbox": [90, 160, 500, 320],
                "confidence": 0.99,
                "status": "VERIFIED"
            }
        ],
        "target_grant": "DARPA Young Faculty Award"
    },
    {
        "id": "paper-21",
        "title": "Real-Time Adaptive Filtering of Motion Artifacts in Unmanned Aerial Biotelemetry",
        "authors": "Adams, R., Rodriguez, M., Hayes, J.",
        "journal": "IEEE Robotics and Automation Letters (RA-L)",
        "year": 2024,
        "doi": "10.1109/LRA.2024.3371902",
        "score": 90,
        "verdict": "Supports",
        "person": "MR",
        "color": "teal",
        "department": "Mechanical Engineering & Robotics",
        "abstract": "Mechanical vibrations during UAV flight introduce severe 10-150 Hz harmonic artifacts into sensor streams. We integrate recursive least-squares adaptive filtering driven by accelerometer reference signals to cancel vibration noise.",
        "claims": [
            {
                "claim_id": "c21-1",
                "text": "Harmonic vibration noise is attenuated by 31.8 dB without degrading target biopotential signal power.",
                "grounding_source": "Figure 7a, page 8",
                "bbox": [105, 120, 490, 330],
                "confidence": 0.95,
                "status": "VERIFIED"
            }
        ],
        "target_grant": "NASA Space Technology Grant"
    },
    {
        "id": "paper-22",
        "title": "Zero-Leakage Gradient Obfuscation via Cryptographic Shuffling",
        "authors": "Lee, J., Scott, T., Rao, S.",
        "journal": "USENIX Security Symposium",
        "year": 2024,
        "doi": "10.5555/3661202",
        "score": 93,
        "verdict": "Supports",
        "person": "JL",
        "color": "blue",
        "department": "EECS",
        "abstract": "We implement hardware-accelerated oblivious shuffling in secure enclaves (Intel SGX and AMD SEV) to break parameter linkability during federated model aggregation.",
        "claims": [
            {
                "claim_id": "c22-1",
                "text": "Oblivious parameter shuffling executes in under 12 ms per 100,000 weights with zero side-channel leakage.",
                "grounding_source": "Section 5.2, page 10",
                "bbox": [80, 190, 480, 350],
                "confidence": 0.98,
                "status": "VERIFIED"
            }
        ],
        "target_grant": "DARPA Young Faculty Award"
    },
    {
        "id": "paper-23",
        "title": "Topological Data Analysis for EEG Latent Trajectory Disambiguation",
        "authors": "Malik, A., Verma, A., Hayes, J.",
        "journal": "PLOS Computational Biology",
        "year": 2023,
        "doi": "10.1371/journal.pcbi.1011409",
        "score": 87,
        "verdict": "Methodology",
        "person": "AM",
        "color": "violet",
        "department": "Helen Wills Neuroscience Institute",
        "abstract": "Persistent homology identifies topological loops and voids in neural dynamical manifolds that correspond to distinct cognitive decision states, providing a coordinate-free metric for cross-subject decoding.",
        "claims": [
            {
                "claim_id": "c23-1",
                "text": "Persistent Betti numbers distinguish 4 motor imagery cognitive classes with 91.2% accuracy without calibration.",
                "grounding_source": "Figure 5, page 7",
                "bbox": [115, 105, 495, 315],
                "confidence": 0.93,
                "status": "VERIFIED"
            }
        ],
        "target_grant": "NIH R21 Neurotechnology"
    },
    {
        "id": "paper-24",
        "title": "Decentralized Clinical Trial Cohort Verification under Multi-Site IRB Mandates",
        "authors": "Rao, S., Miller, D., Vasquez, E.",
        "journal": "The Lancet Digital Health",
        "year": 2024,
        "doi": "10.1016/S2589-7500(24)00092-8",
        "score": 97,
        "verdict": "Supports",
        "person": "SR",
        "color": "teal",
        "department": "Computational Precision Health",
        "abstract": "We evaluate legal and algorithmic compliance across 8 university medical centers participating in federated neuro-prosthetic trials, demonstrating zero patient record transfer while passing multi-site IRB audits.",
        "claims": [
            {
                "claim_id": "c24-1",
                "text": "Zero protected health information (PHI) egresses institutional boundaries across 1,420 clinical trial subjects.",
                "grounding_source": "Audit Table 1, page 5",
                "bbox": [90, 150, 510, 330],
                "confidence": 0.99,
                "status": "VERIFIED"
            }
        ],
        "target_grant": "NSF Smart and Connected Health"
    },
    {
        "id": "paper-25",
        "title": "Micro-Watt Neuromorphic Event-Driven Decoders for Sub-Cranial Implants",
        "authors": "Scott, T., Vance, M., Thorne, M.",
        "journal": "IEEE Solid-State Circuits Letters",
        "year": 2024,
        "doi": "10.1109/LSSC.2024.3359120",
        "score": 91,
        "verdict": "Methodology",
        "person": "TS",
        "color": "orange",
        "department": "EECS",
        "abstract": "Spike-based asynchronous neural decoders consume 18.2 uW total power while processing 64-channel neural spikes, enabling wireless inductive recharge without tissue heating.",
        "claims": [
            {
                "claim_id": "c25-1",
                "text": "Total chip dissipation is constrained to 18.2 uW, maintaining brain tissue temperature rise below 0.05 C.",
                "grounding_source": "Figure 4, page 3",
                "bbox": [100, 110, 480, 310],
                "confidence": 0.96,
                "status": "VERIFIED"
            }
        ],
        "target_grant": "DARPA Young Faculty Award"
    },
    {
        "id": "paper-26",
        "title": "Graph Attention Networks for Cross-Department Collaborative Matchmaking",
        "authors": "Malik, A., Chen, E., Lee, J.",
        "journal": "ACM Transactions on Knowledge Discovery from Data (TKDD)",
        "year": 2024,
        "doi": "10.1145/3669102",
        "score": 94,
        "verdict": "Supports",
        "person": "AM",
        "color": "blue",
        "department": "EECS",
        "abstract": "We construct the campus entity graph over 2,500 nodes (researchers, lab facilities, preprints, and grants). Dual need/offer embedding vectors scored via bilateral graph attention predict fruitful interdisciplinary teams with 94.6% AUC.",
        "claims": [
            {
                "claim_id": "c26-1",
                "text": "Bilateral graph attention achieves 94.6% AUC in predicting funded cross-department grant collaborations.",
                "grounding_source": "Table 4, page 9",
                "bbox": [95, 175, 495, 340],
                "confidence": 0.97,
                "status": "VERIFIED"
            }
        ],
        "target_grant": "NSF Smart and Connected Health"
    },
    {
        "id": "paper-27",
        "title": "Fast Spectral Clamping for Privacy-Preserving Eigenvector Alignment",
        "authors": "Verma, A., Rivera, A., Rao, S.",
        "journal": "Linear Algebra and its Applications",
        "year": 2023,
        "doi": "10.1016/j.laa.2023.09.014",
        "score": 86,
        "verdict": "Methodology",
        "person": "AR",
        "color": "violet",
        "department": "EECS",
        "abstract": "We formulate a fast singular value thresholding algorithm that bounds the sensitivity of covariance eigenvectors under bounded Frobenius perturbation, facilitating differential privacy proofs for PCA.",
        "claims": [
            {
                "claim_id": "c27-1",
                "text": "Eigenvector sensitivity is mathematically bounded by L = 2 / (lambda_k - lambda_{k+1}) under unit perturbation.",
                "grounding_source": "Lemma 2.1, page 4",
                "bbox": [85, 135, 470, 290],
                "confidence": 0.93,
                "status": "VERIFIED"
            }
        ],
        "target_grant": "DOE Advanced Scientific Computing Research"
    },
    {
        "id": "paper-28",
        "title": "Autonomous Airframe Inspection with Continuous Skin-Strain Monitoring",
        "authors": "Rodriguez, M., Adams, R., Thorne, M.",
        "journal": "IEEE Transactions on Industrial Electronics",
        "year": 2024,
        "doi": "10.1109/TIE.2024.3389011",
        "score": 92,
        "verdict": "Supports",
        "person": "MR",
        "color": "violet",
        "department": "Robotics & Autonomous Systems",
        "abstract": "Integrating conductive elastomer strain sensors across carbon-fiber composite wings enables detection of sub-surface micro-cracks under cyclic aerodynamic turbulence.",
        "claims": [
            {
                "claim_id": "c28-1",
                "text": "Micro-cracks down to 25 um depth are detected with 98.2% recall prior to visible surface propagation.",
                "grounding_source": "Figure 8, page 11",
                "bbox": [105, 115, 490, 325],
                "confidence": 0.98,
                "status": "VERIFIED"
            }
        ],
        "target_grant": "NSF CAREER"
    },
    {
        "id": "paper-29",
        "title": "Scalable Vector Search over Pre-Publication Campus Literature",
        "authors": "Lee, J., Chen, E., Malik, A.",
        "journal": "VLDB Endowment (PVLDB)",
        "year": 2024,
        "doi": "10.14778/3651202",
        "score": 95,
        "verdict": "Supports",
        "person": "JL",
        "color": "blue",
        "department": "EECS",
        "abstract": "We benchmark approximate nearest neighbor search over 3,000 pre-prints using HNSW graphs with cosine metric, demonstrating sub-8ms retrieval with 98.4% top-10 recall on a single commodity node.",
        "claims": [
            {
                "claim_id": "c29-1",
                "text": "Top-10 semantic retrieval across 3,000 campus papers completes in 6.4 ms with 98.4% recall.",
                "grounding_source": "Table 2, page 7",
                "bbox": [90, 180, 500, 350],
                "confidence": 0.99,
                "status": "VERIFIED"
            }
        ],
        "target_grant": "DOE Advanced Scientific Computing Research"
    },
    {
        "id": "paper-30",
        "title": "Neural Commons: A Living Knowledge Graph Architecture for University Discovery",
        "authors": "Malik, A., Lee, J., Rodriguez, M., Rao, S., Vasquez, E.",
        "journal": "Communications of the ACM (CACM)",
        "year": 2024,
        "doi": "10.1145/3689102",
        "score": 98,
        "verdict": "Supports",
        "person": "AM",
        "color": "gold",
        "department": "EECS · Helen Wills Neuroscience Institute",
        "abstract": "We present the complete Nexus architecture: a decentralized campus graph connecting 2,500 entities across 97 community clusters, private zero-knowledge hypothesis vaults, and autonomous grant synthesis with citation audit trails.",
        "claims": [
            {
                "claim_id": "c30-1",
                "text": "Nexus reduces cross-department collaborator discovery time from 14 months to under 3 days.",
                "grounding_source": "Figure 1, Executive Overview, page 2",
                "bbox": [100, 90, 480, 310],
                "confidence": 0.99,
                "status": "VERIFIED"
            },
            {
                "claim_id": "c30-2",
                "text": "Grant proposal draft readiness moves from 35% to 80% with automated citation and figure verification.",
                "grounding_source": "Section 4.3, Metric Evaluation, page 8",
                "bbox": [90, 195, 495, 360],
                "confidence": 0.98,
                "status": "VERIFIED"
            }
        ],
        "target_grant": "NSF Smart & Connected Communities"
    }
]

# Write outputs
with open(os.path.join(DATA_DIR, "demo_profiles.json"), "w", encoding="utf-8") as f:
    json.dump(PROFILES, f, indent=2)
print(f"✔ Exported {len(PROFILES)} demo researcher profiles to data/demo_profiles.json")

with open(os.path.join(DATA_DIR, "demo_parsed_papers.json"), "w", encoding="utf-8") as f:
    json.dump(PAPERS, f, indent=2)
print(f"✔ Exported {len(PAPERS)} deeply parsed scientific papers with claims and figure bounding boxes to data/demo_parsed_papers.json")
