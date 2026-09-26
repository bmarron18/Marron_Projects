from pathlib import Path
skill_path = Path("/home/oai/skills/pdfs/skill.md")
skill_instructions = skill_path.read_text() if skill_path.exists() else None
print("Preparing the downloadable concept diagram and design brief.")
