// Enforcement gate: hardcoded strings in customer-facing JSX are a CI failure.
// Scope: src/app/routes/app/** only (customer surface, not admin/legacy).
// Covers JSX text content and key attributes (label, placeholder, aria-label).
// Uses only @typescript-eslint/parser (for TSX) + eslint-plugin-i18next.
// @typescript-eslint/eslint-plugin is intentionally excluded (ESLint 9 peer conflict).
import tsParser from "@typescript-eslint/parser";
import i18nextPlugin from "eslint-plugin-i18next";

export default [
  {
    ignores: ["dist/**", "node_modules/**", "src/pages/**"],
  },
  {
    files: ["src/app/routes/app/**/*.{ts,tsx}"],
    plugins: {
      i18next: i18nextPlugin,
    },
    languageOptions: {
      parser: tsParser,
      parserOptions: {
        ecmaFeatures: { jsx: true },
      },
    },
    rules: {
      "i18next/no-literal-string": [
        "error",
        {
          mode: "jsx-only",
          "jsx-attributes": {
            include: ["label", "placeholder", "title", "aria-label", "alt"],
          },
        },
      ],
    },
  },
];
