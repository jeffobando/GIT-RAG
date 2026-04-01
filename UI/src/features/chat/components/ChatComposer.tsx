import { useState, type FormEvent } from "react";

import { Button } from "../../../components/ui/Button";

export function ChatComposer({
  onSubmit,
  loading,
}: {
  onSubmit: (question: string) => Promise<void> | void;
  loading: boolean;
}) {
  const [question, setQuestion] = useState("");

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const value = question.trim();
    if (!value || loading) {
      return;
    }
    await onSubmit(value);
    setQuestion("");
  };

  return (
    <form onSubmit={handleSubmit} className="rounded-xl border border-slate-200 bg-white p-4 shadow-panel">
      <label htmlFor="question" className="mb-2 block text-sm font-medium text-slate-700">
        Haz una pregunta
      </label>
      <div className="flex flex-col gap-3 md:flex-row">
        <textarea
          id="question"
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder="Ej: ¿Cómo debo nombrar una rama para corregir un bug?"
          className="min-h-[72px] flex-1 resize-y rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none transition focus:border-slate-500"
        />
        <Button type="submit" disabled={loading} className="md:h-fit md:self-end">
          {loading ? "Generando..." : "Enviar"}
        </Button>
      </div>
    </form>
  );
}
