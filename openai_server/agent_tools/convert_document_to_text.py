import argparse
import os
import sys
import json
import uuid

if 'src' not in sys.path:
    sys.path.append('src')

from src.function_client import get_data_h2ogpt


def has_gpu():
    import subprocess
    try:
        result = subprocess.run(['nvidia-smi'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False


def process_files(files):
    text_context_list = []

    textual_types = ('.txt', '.csv', '.toml', '.py', '.rst', '.rtf', '.md', '.html', '.htm', '.xml', '.json', '.yaml',
                     '.yml', '.ini', '.log', '.tex', '.sql', '.sh', '.bat', '.js', '.css', '.php', '.jsp', '.pl', '.r',
                     '.lua', '.conf', '.properties', '.tsv', '.xhtml', '.srt', '.vtt', '.cpp', '.c', '.h', '.go')

    doc_types = ('.pdf', '.docx', '.doc', '.epub', '.pptx', '.ppt', '.xls', '.xlsx')

    for filename in files:
        if filename.lower().endswith(textual_types):
            with open(filename, "rt") as f:
                text_context_list.append(f.read())
        elif filename.lower().endswith(doc_types):
        # else:
            # have_gpu = has_gpu()
            have_gpu = False  # too slow for now

            sources1, known_type = get_data_h2ogpt(filename,
                                                   verbose=False,
                                                   use_unstructured_pdf='off',
                                                   enable_pdf_ocr='off',
                                                   enable_pdf_doctr='off' if not have_gpu else 'on',
                                                   enable_captions=have_gpu,
                                                   enable_llava=False,
                                                   chunk=False,
                                                   enable_transcriptions=have_gpu)

            if not sources1:
                print(f"Unable to handle file type for {filename}")
            else:
                text_context_list.extend([x.page_content for x in sources1])
        else:
            print(f"Unable to handle file type for {filename}")

    return text_context_list


def main():
    parser = argparse.ArgumentParser(description="Converts document to text")
    parser.add_argument("--files", nargs="+", required=True, help="Files to convert to text")
    parser.add_argument("--output", type=str, required=False, help="Output filename")
    args = parser.parse_args()

    if not args.output:
        args.output = f"conversion_to_text_{str(uuid.uuid4())[:6]}.txt"

    text_context_list = process_files(args.files)

    # Join the text_context_list into a single string
    output_text = "\n\n".join(text_context_list)

    # Write the output to the specified file
    with open(args.output, "w") as f:
        f.write(output_text)

    print(f"{args.files} has been converted to text and written to {args.output}")


if __name__ == "__main__":
    main()
