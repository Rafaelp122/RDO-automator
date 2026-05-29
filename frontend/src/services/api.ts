import type { SourcePreviewResponse, TemplatePreviewResponse, GenerateConfig } from "../types";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export async function previewSource(file: File): Promise<SourcePreviewResponse> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${API_URL}/api/preview/source`, { method: "POST", body: form });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Erro ao enviar arquivo de origem");
  }
  return res.json();
}

export async function previewTemplate(file: File): Promise<TemplatePreviewResponse> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${API_URL}/api/preview/template`, { method: "POST", body: form });
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
): Promise<Blob> {
  const form = new FormData();
  form.append("source", source);
  form.append("template", template);
  form.append("config", JSON.stringify(config));

  const res = await fetch(`${API_URL}/api/generate`, { method: "POST", body: form });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Erro ao gerar relatorio");
  }
  return res.blob();
}
