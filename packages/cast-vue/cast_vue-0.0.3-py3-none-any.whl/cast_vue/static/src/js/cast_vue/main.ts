import '../../css/cast_vue/styles.css';
import '../../css/cast_vue/pygments.css';
import 'vite/modulepreload-polyfill';  // recommended by django-vite, dunno why

import { createApp } from 'vue';
import { createPinia } from 'pinia';
import { createRouter, createWebHistory } from "vue-router";
import LoadPostList from "./components/LoadPostList.vue";
import Counter from "./components/Counter.vue";
import PostDetail from "./components/PostDetail.vue";

import App from './App.vue';

const routes = [
    {
        path: "/",
        name: "PostList",
        component: LoadPostList,
    },
    {
        path: "/:slug/",
        name: "PostDetail",
        component: PostDetail,
    },
    {
        path: "/counter",
        name: "Counter",
        component: Counter,
    },
];

let baseUrl = "/";
const baseUrlElement = document.getElementById("base-url");
if (baseUrlElement?.textContent) {
    baseUrl = JSON.parse(baseUrlElement.textContent);
}
const router = createRouter({
    history: createWebHistory(baseUrl),
    routes,
  });

const app = createApp(App)
app.use(router);

const pinia = createPinia()
app.use(pinia);

app.mount("#app")
