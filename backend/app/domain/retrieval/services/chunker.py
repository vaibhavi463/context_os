import re


class RecursiveTextChunker:
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 64) -> None:
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_text(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []

        # Normalize line endings
        text = text.replace("\r\n", "\n")
        
        # Paragraph splitting
        paragraphs = re.split(r'\n\s*\n', text)
        chunks: list[str] = []
        current_chunk: list[str] = []
        current_length = 0

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            para_len = len(para.split())
            if current_length + para_len <= self.chunk_size:
                current_chunk.append(para)
                current_length += para_len
            else:
                if current_chunk:
                    chunks.append("\n\n".join(current_chunk))
                
                # If paragraph itself exceeds chunk_size, split by sentences
                if para_len > self.chunk_size:
                    sentences = re.split(r'(?<=[.!?])\s+', para)
                    sub_chunk: list[str] = []
                    sub_len = 0
                    for sent in sentences:
                        sent_len = len(sent.split())
                        if sub_len + sent_len <= self.chunk_size:
                            sub_chunk.append(sent)
                            sub_len += sent_len
                        else:
                            if sub_chunk:
                                chunks.append(" ".join(sub_chunk))
                            sub_chunk = [sent]
                            sub_len = sent_len
                    if sub_chunk:
                        current_chunk = sub_chunk
                        current_length = sub_len
                else:
                    current_chunk = [para]
                    current_length = para_len

        if current_chunk:
            chunks.append("\n\n".join(current_chunk))

        # Handle overlaps if necessary
        return chunks
