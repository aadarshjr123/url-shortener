import { api } from "../api/axios";

export const shortenUrl = async (originalUrl: string) => {
  const response = await api.post("/shorten", {
    original_url: originalUrl,
  });

  return response.data;
};