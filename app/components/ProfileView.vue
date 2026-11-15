<script setup lang="ts">
import { ref } from "vue";
import ProfileForm from "./ProfileForm.vue";
import ExperienceList from "./ExperienceList.vue";
import EducationList from "./EducationList.vue";
import CourseList from "./CourseList.vue";
import SkillList from "./SkillList.vue";
import LinkList from "./LinkList.vue";
import ProjectList from "./ProjectList.vue";
import ResumeGenerator from "./ResumeGenerator.vue";

type Tab =
  | "personal"
  | "experience"
  | "education"
  | "courses"
  | "projects"
  | "skills"
  | "links"
  | "resume";

const active = ref<Tab>("personal");

const tabs: { key: Tab; label: string }[] = [
    { key: "personal", label: "Dados Pessoais" },
    { key: "experience", label: "Experiências" },
    { key: "education", label: "Formação" },
    { key: "courses", label: "Cursos" },
    { key: "projects", label: "Projetos" },
    { key: "skills", label: "Habilidades" },
    { key: "links", label: "Links" },
    { key: "resume", label: "Currículo" },
];
</script>

<template>
    <div class="profile-view">
        <nav class="tabs">
            <button v-for="t in tabs" :key="t.key" :class="{ active: active === t.key }" @click="active = t.key">
                {{ t.label }}
            </button>
        </nav>
        <section class="tab-content">
            <ProfileForm v-if="active === 'personal'" />
            <ExperienceList v-else-if="active === 'experience'" />
            <EducationList v-else-if="active === 'education'" />
            <CourseList v-else-if="active === 'courses'" />
            <ProjectList v-else-if="active === 'projects'" />
            <SkillList v-else-if="active === 'skills'" />
            <LinkList v-else-if="active === 'links'" />
            <ResumeGenerator v-else-if="active === 'resume'" />
        </section>
    </div>
</template>

<style scoped>
.profile-view {
    max-width: 780px;
    margin: 0 auto;
    padding: 1rem 1.5rem 3rem;
}

.tabs {
    display: flex;
    gap: 0.25rem;
    border-bottom: 2px solid #e0e0e0;
    margin-bottom: 1.25rem;
    overflow-x: auto; /* Previne quebra se a tela for pequena */
}

.tabs button {
    background: transparent;
    border: 0;
    padding: 0.7rem 0.8rem;
    cursor: pointer;
    font-size: 0.95rem;
    color: #666;
    border-bottom: 2px solid transparent;
    margin-bottom: -2px;
    white-space: nowrap;
}

.tabs button.active {
    color: #1f1f1f;
    font-weight: 600;
    border-bottom-color: #7a1fa2;
}

.tabs button:hover:not(.active) {
    color: #333;
}
</style>