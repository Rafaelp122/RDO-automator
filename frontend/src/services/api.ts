import type { SourcePreviewResponse, TemplatePreviewResponse, GenerateConfig } from "../types";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
const API_KEY = import.meta.env.VITE_API_KEY || "";

function headers(): Record<string, string> {
  return API_KEY ? { "X-API-Key": API_KEY } : {};
}

export async function previewSource(file: File, headerRow: number = 0): Promise<SourcePreviewResponse> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${API_URL}/api/preview/source?header_row=${headerRow}`, {
    method: "POST",
    body: form,
    headers: headers(),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Erro ao enviar arquivo de origem");
  }
  return res.json();
}

export async function previewTemplate(file: File): Promise<TemplatePreviewResponse> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${API_URL}/api/preview/template`, {
    method: "POST",
    body: form,
    headers: headers(),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Erro ao enviar template");
  }
  return res.json();
}

export async function generateReport(
  source: File,
  template: File,
  config: GenerateConfig,
  headerRow: number = 0,
): Promise<Blob> {
  const form = new FormData();
  form.append("source", source);
  form.append("template", template);
  form.append("config", JSON.stringify(config));
  form.append("header_row", String(headerRow));

  const res = await fetch(`${API_URL}/api/generate`, {
    method: "POST",
    body: form,
    headers: headers(),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Erro ao gerar relatorio");
  }
  return res.blob();
}
