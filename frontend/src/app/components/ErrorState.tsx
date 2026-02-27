// EVA-STORY: ACA-05-031
import { MessageBar, MessageBarBody, Button } from "@fluentui/react-components";

interface Props {
  message: string;
  detail?: string;
  onRetry?: () => void;
}

export function ErrorState({ message, detail, onRetry }: Props) {
  return (
    <MessageBar intent="error" role="alert" style={{ marginBlock: 16 }}>
      <MessageBarBody>
        <strong>{message}</strong>
        {detail && <div style={{ marginTop: 4, fontSize: 13, opacity: 0.85 }}>{detail}</div>}
        {onRetry && (
          <Button
            appearance="subtle"
            size="small"
            onClick={onRetry}
            style={{ marginTop: 8 }}
          >
            Try again
          </Button>
        )}
      </MessageBarBody>
    </MessageBar>
  );
}
