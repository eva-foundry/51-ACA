import React from "react";

export function SearchBar({
  value,
  onChange,
  onSubmit,
  placeholder = "Search…",
}: {
  value: string;
  onChange: (v: string) => void;
  onSubmit: () => void;
  placeholder?: string;
}) {
  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        onSubmit();
      }}
      style={{ display: "flex", gap: 8, alignItems: "center" }}
    >
      <input
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        style={{ padding: 10, borderRadius: 8, border: "1px solid #ccc", width: 380 }}
      />
      <button type="submit" style={{ padding: "10px 14px", borderRadius: 8, border: "1px solid #ccc" }}>
        Search
      </button>
    </form>
  );
}
