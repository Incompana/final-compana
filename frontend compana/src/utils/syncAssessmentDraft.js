import api from "../api/axios";

export const syncAssessmentDraft = async () => {
  const savedDraft = localStorage.getItem("assessment_draft");

  if (!savedDraft) return false;

  const draft = JSON.parse(savedDraft);

  if (!draft?.assessmentPayload) return false;

  await api.post(
    "/assessments/save",
    draft.assessmentPayload
  );

  localStorage.removeItem("assessment_draft");

  return true;
};