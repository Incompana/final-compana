import {
  createContext,
  useContext,
  useEffect,
  useState,
} from "react";

const AssessmentContext = createContext();

const initialState = {
  inputText: "",
  answers: {},
  analysisResult: null,
  skillGap: null,
};

export function AssessmentProvider({ children }) {
  const [draft, setDraft] = useState(() => {
    const saved = localStorage.getItem(
      "assessment_draft"
    );

    return saved
      ? JSON.parse(saved)
      : initialState;
  });

  useEffect(() => {
    localStorage.setItem(
      "assessment_draft",
      JSON.stringify(draft)
    );
  }, [draft]);

  const clearDraft = () => {
    localStorage.removeItem("assessment_draft");
    setDraft(initialState);
  };

  return (
    <AssessmentContext.Provider
      value={{
        draft,
        setDraft,
        clearDraft,
      }}
    >
      {children}
    </AssessmentContext.Provider>
  );
}

export const useAssessment = () =>
  useContext(AssessmentContext);