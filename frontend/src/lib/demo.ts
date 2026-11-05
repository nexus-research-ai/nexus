import { demoEvidenceByKey } from './demoEvidence';

export type CollaborationAvailability = { capstone: boolean; coauthor: boolean; mentor: boolean; equipment: boolean };
export const defaultAvailability: CollaborationAvailability = { capstone: true, coauthor: true, mentor: false, equipment: false };

export const currentDemoProfileId = 'user-aria';

export const projectOwners = [
  { ownerId: 'user-aria', owner: 'Aria Malik', initials: 'AM', resource: 'Federated EEG baseline · PyTorch adapters' },
  { ownerId: 'user-maya', owner: 'Maya Rodriguez', initials: 'MR', resource: 'Soft sensor hardware · Field recordings' },
  { ownerId: 'user-sarah', owner: 'Sarah Rao', initials: 'SR', resource: 'Clinical cohort dataset · Privacy evaluation' },
  { ownerId: 'user-marcus', owner: 'Marcus Vance', initials: 'MV', resource: 'Synchronized biosignal dataset · Sensor rigs' },
  { ownerId: 'user-jordan', owner: 'Jordan Lee', initials: 'JL', resource: '128-channel mobile EEG dataset · Auditory tasks' },
  { ownerId: 'user-emily', owner: 'Emily Chen', initials: 'EC', resource: 'Scientific figure dataset · Microscopy images' },
  { ownerId: 'user-david', owner: 'David Miller', initials: 'DM', resource: 'Single-cell RNA-seq and ATAC-seq datasets' },
  { ownerId: 'user-tyler', owner: 'Tyler Scott', initials: 'TS', resource: 'Low-power recording hardware · FPGA testbed' },
];

export const demoFeed = [
  { id: 'eeg-benchmark', initials: 'JL', author: 'Jordan Lee', role: 'PhD Researcher · Neuroscience', time: '25 min ago', stage: 'Dataset available', title: 'Looking for a federated learning partner for mobile EEG', body: 'Our mobile EEG pipeline is ready for a cross-subject benchmark. I can offer 128-channel recordings, event markers, and a preprocessing notebook. Looking for someone who can help evaluate a shared model without centralizing the recordings.', offer: ['128-channel mobile EEG', 'Preprocessing notebooks'], need: ['Federated learning', 'Privacy evaluation'], comments: [{ author: 'Aria Malik', text: 'This fits our latent alignment project. Can we start by comparing channel maps and task labels?' }, { author: 'Jordan Lee', text: 'Yes. I can share the data dictionary and a small example after we connect.' }] },
  { id: 'figure-grounding', initials: 'EC', author: 'Emily Chen', role: 'PhD Student · Computer Vision', time: '1h ago', stage: 'Seeking collaborators', title: 'Building a benchmark for reading scientific figures', body: 'I’m assembling a small evaluation set for figure captions, axis labels, and sub-panel references. Looking for researchers who can contribute annotated microscopy or neural spectrogram examples.', offer: ['Image segmentation', 'Annotation tooling'], need: ['Figure examples', 'Domain reviewers'], comments: [{ author: 'Sarah Rao', text: 'Happy to help review the clinical terminology and define an annotation checklist.' }] },
  { id: 'student-reproducibility', initials: 'AM', author: 'Aria Malik', role: 'MS Computer Science · RIT', time: 'Yesterday', stage: 'Research update', title: 'A reproducible starting point for privacy-preserving neural decoding', body: 'The first baseline is organized into preprocessing, training, and evaluation notebooks. Next up: a subject-held-out split and a clear comparison between local and federated training. Open to capstone teams and co-authoring.', offer: ['PyTorch baseline', 'Federated evaluation'], need: ['Longitudinal EEG', 'Methods feedback'], comments: [{ author: 'Tyler Scott', text: 'I can help profile memory use on an edge device once the baseline is ready.' }] },
  { id: 'cohort-data', initials: 'DM', author: 'David Miller', role: 'Research Scientist · Computational Biology', time: 'Yesterday', stage: 'Dataset collaboration', title: 'Comparing single-cell cohorts across research groups', body: 'We are preparing a common data dictionary for RNA-seq and ATAC-seq experiments. Seeking a collaborator to test representation alignment and document where batch effects change the conclusions.', offer: ['Single-cell analysis', 'Example data dictionary'], need: ['Representation learning', 'Reproducibility review'], comments: [{ author: 'Emily Chen', text: 'The annotation workflow may overlap with our benchmark tooling. Let’s compare schemas.' }] },
  { id: 'grant-planning', initials: 'SR', author: 'Sarah Rao', role: 'Faculty · Privacy & Computational Health', time: '2 days ago', stage: 'Team forming', title: 'Planning an exploratory proposal for distributed health research', body: 'Before drafting, we are collecting a focused research question, a feasible pilot, and a list of data-access dependencies. Looking for students interested in privacy methods, study design, and literature review.', offer: ['Proposal mentoring', 'Study design review'], need: ['Pilot experiments', 'Literature review'], comments: [{ author: 'Aria Malik', text: 'I can contribute the federated baseline and a first pass at the evaluation plan.' }] },
];

export function demoConversations() {
  const now = Date.now();
  type EvidenceKey = keyof typeof demoEvidenceByKey;
  type Turn = { prompt: string; answer: string; evidence: EvidenceKey[] };
  const threads: { id: string; title: string; turns: Turn[] }[] = [
    {
      id: 'demo-chat-eeg', title: 'Planning a federated EEG pilot', turns: [
        { prompt: 'How should Jordan and I plan a first federated EEG experiment?', answer: 'A useful first study would compare local training with a federated baseline on one agreed EEG task. The imported EEG defense paper studies poisoning resistance in federated EEG classification; it motivates checking robustness as well as predictive performance. For our proposed pilot, agree on the task, channel mapping, labels, and evaluation protocol before training. We have not run this experiment or established a performance gain.', evidence: ['eegDefense'] },
        { prompt: 'How should we split the data without leaking subjects between training and evaluation?', answer: 'For our proposed study, assign participants to training, validation, and test groups before constructing windows. Keep each participant’s sessions within their assigned group, and fit preprocessing only on training data. Report per-participant performance and document differences between sites. This is our evaluation recommendation, not a split verified from the cited paper. The communication paper describes learning across workers without sharing training data; that does not by itself prevent subject leakage in an evaluation.', evidence: ['communication'] },
        { prompt: 'What should Jordan and I do next?', answer: `1. Ask Jordan for a data dictionary and the permitted uses of the recordings.
2. Agree on participant grouping, task labels, and a small reproducible local baseline.
3. Specify how we will compare federated training, communication cost, and robustness.
4. Review access controls and a poisoning threat model before exchanging updates.
The paper’s defense is a method to examine, not a validated result for our project. The excerpt below is a source claim; this checklist is our proposed next work.`, evidence: ['eegDefense'] },
      ],
    },
    {
      id: 'demo-chat-datasets', title: 'Questions to ask before using a dataset', turns: [
        { prompt: 'What should I ask Jordan before using the EEG dataset?', answer: 'Request consent and reuse conditions, participant and session counts, channel layout, sample rate, event labels, missing-data notes, and the preprocessing history. Confirm who can authorize access and whether a de-identified example is available. These are proposed due-diligence questions; no dataset access has been approved here. Federated learning can avoid direct training-data exchange, but the cited privacy paper describes why model updates can still disclose information.', evidence: ['fragmentedPrivacy'] },
        { prompt: 'If raw recordings stay in the lab, is that enough to call the study private?', answer: 'No. The fragmented-update paper identifies privacy risks from model updates and integrity risks from poisoned updates. Its proposed encrypted-fragment approach is one defense to investigate, not proof that our study is private. Define the adversary, what each participant can observe, how updates are protected, and what is logged. Do not claim differential privacy unless a concrete mechanism and privacy accounting justify it.', evidence: ['fragmentedPrivacy'] },
        { prompt: 'Give me a short checklist for our dataset handoff meeting.', answer: 'Confirm permitted use and the approving contact; compare the data dictionary with a small approved example; document participant-level splits; map the path of recordings, updates, and logs; and assign a reviewer for privacy and poisoning risks. Record unresolved access questions before training begins. The cited excerpt supports reviewing update leakage; it does not certify consent, anonymity, or compliance for Jordan’s recordings.', evidence: ['fragmentedPrivacy'] },
      ],
    },
    {
      id: 'demo-chat-grant', title: 'A first outline for the Neural Commons proposal', turns: [
        { prompt: 'Help me outline an exploratory research proposal for this collaboration.', answer: 'Draft six sections: research question, motivation, specific aims, methods, evaluation, and team responsibilities. A possible question is how to evaluate cross-site EEG models while keeping training data with each lab. The communication paper provides a methodological starting point for discussing distributed optimization and communication. It does not establish that our team is eligible for a grant, or that any funding program is currently open.', evidence: ['communication'] },
        { prompt: 'Can we separate the aims from what the papers already establish?', answer: 'Yes. Proposed Aim 1: document a local EEG baseline and participant-held-out evaluation. Proposed Aim 2: measure the effect of federated updates and communication constraints. Proposed Aim 3: review robustness and data-access risks. The multi-objective paper studies clients with different objective functions and communication-saving local updates. Cite that as related methodology; our EEG aims, feasibility, and outcomes remain to be tested.', evidence: ['multiObjective'] },
        { prompt: 'What funding details can I safely put in the draft today?', answer: 'Describe the question, pilot plan, methods references, dependencies, and who will perform each task. Mark the target agency, solicitation, budget ceiling, eligibility, deadline, and required approvals as unverified until you inspect the current official call. The paper below supports only the methods discussion. It supplies no evidence of an award, funding commitment, or program eligibility for Neural Commons.', evidence: ['communication'] },
      ],
    },
    {
      id: 'demo-chat-literature', title: 'Literature review search plan', turns: [
        { prompt: 'How can I organize an artificial intelligence literature search around our EEG idea?', answer: 'Start with three branches: federated learning methods, EEG classification and robustness, and privacy of shared updates. The imported multi-objective paper studies optimization when clients have different objectives; the EEG defense paper studies poisoning resistance in EEG classification. These are concrete starting points from the imported corpus, not a complete review or a claim that either method transfers successfully to our recordings.', evidence: ['multiObjective', 'eegDefense'] },
        { prompt: 'How should I compare the methods without overstating the evidence?', answer: 'Build a table with task, data distribution, client objective, communication assumptions, threat model, evaluation protocol, and limitations. For the multi-objective paper, record its focus on different client objectives. For the fragmented-update paper, record update privacy and poisoning concerns. Check the original full texts before filling in datasets, numeric results, or implementation details that the imported abstracts do not establish.', evidence: ['multiObjective', 'fragmentedPrivacy'] },
        { prompt: 'What should go into my literature review notes right now?', answer: 'Save each title and original source link, quote the relevant abstract passage, and keep three separate columns: what the source claims, what we infer, and what our pilot must test. Record the communication paper as a candidate reference for communication-efficient federated optimization. Do not report its method as our implementation or its findings as our results. The excerpt below is evidence from the imported source record; confirm details in the original paper before citation.', evidence: ['communication'] },
      ],
    },
  ];
  return threads.map((thread, index) => ({
    id: thread.id, title: thread.title, demo: true,
    updatedAt: new Date(now - (index + 1) * 3600000).toISOString(),
    messages: thread.turns.flatMap((turn, turnIndex) => {
      const citations = turn.evidence.map(key => demoEvidenceByKey[key]);
      const excerpts = citations.map(citation => `Source excerpt — ${citation.title}: “${citation.quote}”`).join('\n\n');
      return [
        { id: `${thread.id}-user-${turnIndex + 1}`, role: 'user' as const, content: turn.prompt },
        { id: `${thread.id}-reply-${turnIndex + 1}`, role: 'assistant' as const, content: `${turn.answer}\n\n${excerpts}`, citations },
      ];
    }),
  }));
}
