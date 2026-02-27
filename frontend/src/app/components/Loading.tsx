import { Spinner } from "@fluentui/react-components";

interface Props {
  label?: string;
  inline?: boolean;
}

export function Loading({ label = "Loading...", inline = false }: Props) {
  return (
    <div
      role="status"
      aria-label={label}
      style={
        inline
          ? { display: "inline-flex", alignItems: "center", gap: 8 }
          : {
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
              minHeight: 120,
            }
      }
    >
      <Spinner size={inline ? "tiny" : "medium"} label={label} />
    </div>
  );
}
