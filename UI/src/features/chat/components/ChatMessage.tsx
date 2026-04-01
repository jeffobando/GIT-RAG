import { useAdminMode } from "../../../app/admin-mode";
import type { ChatExchange } from "../../../app/query-session";
import { Card, CardBody, CardHeader } from "../../../components/ui/Card";
import { SourceCard } from "./SourceCard";

export function ChatMessage({ exchange }: { exchange: ChatExchange }) {
  const { isAdminMode } = useAdminMode();

  return (
    <Card>
      <CardHeader>
        <p className="text-xs font-medium uppercase tracking-wide text-slate-500">Pregunta</p>
        <p className="mt-2 text-sm text-slate-900">{exchange.question}</p>
      </CardHeader>
      <CardBody>
        <p className="text-xs font-medium uppercase tracking-wide text-slate-500">Respuesta</p>
        <p className="mt-2 whitespace-pre-wrap text-sm leading-6 text-slate-800">{exchange.response.answer}</p>

        {isAdminMode && exchange.response.sources.length > 0 && (
          <div className="mt-5 space-y-3">
            <p className="text-xs font-medium uppercase tracking-wide text-slate-500">Fuentes</p>
            {exchange.response.sources.map((source, index) => (
              <SourceCard key={`${exchange.id}-${index}`} source={source} />
            ))}
          </div>
        )}
      </CardBody>
    </Card>
  );
}

