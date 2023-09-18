import argparse
import json
import random

translation_dict = {
    'ą': 'a',
    'ć': 'c',
    'ę': 'e',
    'ł': 'l',
    'ń': 'n',
    'ó': 'o',
    'ś': 's',
    'ż': 'z',
    'ź': 'z'
}

def remove_polish_characters(word):
    return ''.join(translation_dict.get(char, char) for char in word)

def process_words(words):
    no_pl_char_words = list(map(lambda wrd: remove_polish_characters(wrd), words))
    return list(set(no_pl_char_words))

def generate_passwords(file_name, num_passwords):
    with open(file_name, encoding='utf-8') as f:
        words = json.load(f)
        words = process_words(words)

    used_words = []

    # Generate the specified number of passwords
    pawwsords = []
    for _ in range(num_passwords):
        pawwsords.append(generate_password(words, used_words))

    return pawwsords

def gen_pass(chosen_words: list[str]):
    password = chosen_words[0].lower()
    password += chosen_words[1].title()
    password += chosen_words[2].title()
    password += str(random.randint(0, 9))
    password += str(random.randint(0, 9))
    password += random.choice("_+-,.")
    return password


def generate_password(words, used_words):
    available_words = [word for word in words if word not in used_words]
    if len(available_words) < 3:
        raise ValueError("Not enough words in the array to generate a password")

    chosen_words = random.sample(available_words, 3)
    used_words += chosen_words
    return gen_pass(chosen_words)

from fpdf import FPDF
def generate_pdf(passwords):
#     pdf = FPDF()
#     pdf.set_auto_page_break(auto=1, margin=15)
#     pdf.add_page()
#     pdf.set_font("Arial", size=12)

#     # Dodanie tytułu
#     pdf.cell(200, 10, "Wygenerowane hasła", ln=1, align="C")

#     # Dodanie haseł do PDF-a
#     for idx, password_entry in enumerate(passwords):
#         pdf.cell(0, 10, f"{idx+1}. {password_entry}", ln=1)

# # Zapisanie PDF-a do pliku
#     pdf_output_path = "fs/out/passwords.pdf"
#     pdf.output(name=pdf_output_path, dest="F")

    pdf = FPDF()
    pdf.set_auto_page_break(auto=1, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Dodanie tytułu
    pdf.cell(200, 10, "Wygenerowane hasla", ln=1, align="C")

    # Dodanie haseł do PDF-a, tym razem zabezpieczając je przed problemami z kodowaniem
    for idx, password_entry in enumerate(passwords):
        safe_password_entry = remove_polish_characters(password_entry)
        pdf.cell(0, 10, f"{idx+1}. {safe_password_entry}", ln=1)

    # Zapisanie PDF-a do pliku
    pdf_output_path = "fs/out/passwords.pdf"
    pdf.output(name=pdf_output_path, dest="F")

def js_format(passwds):
    pass_line = list(map(lambda pwd: f"{{ password: '{pwd}', inUse: false }}", passwds))
    array_str = ",\n        ".join(pass_line)
    whole_str = f"this.password_idx = [\n        {array_str}\n    ]"
    return whole_str

if __name__ == "__main__":
    # Parse the command line arguments
    parser = argparse.ArgumentParser(description="Generate passwords from a JSON file")
    parser.add_argument("file_name", help="the name of the JSON file containing the array of words")
    parser.add_argument("num_passwords", type=int, help="the number of passwords to generate")
    args = parser.parse_args()

    # Generate the passwords
    passwords = generate_passwords(args.file_name, args.num_passwords)
    js_format_str = js_format(passwords)
    print(js_format_str)
    generate_pdf(passwords)