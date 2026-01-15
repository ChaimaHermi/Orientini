export interface ChatResponse {
  answer: string;

  conversation_id: string;
  conversation_title: string;

  // 🔹 MuRAG (images éventuelles)
  images?: {
    [entityId: string]: string[];
  };
}
