<template>
  <div>
    <router-view></router-view>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import { getTexContentFromElement } from './helpers/dom';

const router = useRouter();
const vueRouteName = getTexContentFromElement("vue-route-name");

function getQueryParameters() {
  const searchParams = new URLSearchParams(window.location.search);
  const params: Record<string, any> = {};
  searchParams.forEach((value, key) => {
    if (params.hasOwnProperty(key)) {
      if (Array.isArray(params[key])) {
        params[key].push(value);
      } else {
        params[key] = [params[key], value];
      }
    } else {
      params[key] = value;
    }
  });
  return params;
}

if (vueRouteName == "PostDetail") {
  const slug = getTexContentFromElement("slug");
  router.push({ name: vueRouteName, params: { slug: slug } })
} else {
  // get query params from URL and push them to router
  const params: Record<string, any> = getQueryParameters();
  router.push({ name: vueRouteName, query: params });
}
</script>
