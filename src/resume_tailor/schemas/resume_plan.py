from dataclasses import dataclass, field


@dataclass
class Contact:
    email: str = ""
    phone: str = ""
    website: str = ""
    linkedin: str = ""
    github: str = ""


@dataclass
class EducationItem:
    institution: str
    degree: str
    dates: str
    location: str = ""
    thesis: str = ""


@dataclass
class ExperienceItem:
    company: str
    role: str
    dates: str
    location: str = ""
    bullets: list[str] = field(default_factory=list)


@dataclass
class ProjectItem:
    name: str
    kind: str = ""  # "Course Project" / "Research Project" / "Open Source"
    url: str = ""
    bullets: list[str] = field(default_factory=list)


@dataclass
class Publication:
    title: str
    venue: str = ""  # "INFORMATIK 2022", "arXiv:2005.11288"


@dataclass
class ResumePlan:
    name: str
    summary: str = ""
    contact: Contact = field(default_factory=Contact)
    education: list[EducationItem] = field(default_factory=list)
    experience: list[ExperienceItem] = field(default_factory=list)
    skills: dict[str, list[str]] = field(default_factory=dict)
    projects: list[ProjectItem] = field(default_factory=list)
    publications: list[Publication] = field(default_factory=list)
    spoken_languages: list[str] = field(default_factory=list)
