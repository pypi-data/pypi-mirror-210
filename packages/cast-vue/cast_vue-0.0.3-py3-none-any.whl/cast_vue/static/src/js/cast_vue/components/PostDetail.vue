<template>
  <div>
    <p v-if="isLoading">Loading data...</p>
    <div v-else>
      <router-link to="/">Back to Blog</router-link>
      <post-item :post="post" :detail="true"></post-item>
    </div>
  </div>
</template>

<script lang="ts">
import { useRoute } from 'vue-router';
import PostItem from './PostItem.vue';
import { useDataStore } from '../stores/dataStore';
import { Post } from './types';
import { ref, onMounted } from 'vue';
import { getWagtailApiBaseUrl } from '../helpers/dom';

export default {
  name: "PostDetail",
  components: {
    PostItem,
  },
  setup() {
    const route = useRoute();
    const dataStore = useDataStore();
    const wagtailApiUrl = getWagtailApiBaseUrl();

    const isLoading = ref(true);
    const post = ref({} as Post);
    const visibleDateStr = ref("");

    const fetchPostFromAPI = async () => {
      const postSlug = route.params.slug as string;
      // FIXME maybe use clean detail url? But then we need to have
      // the page id instead of the slug and and either modify the API
      // to accept slugs or do a second request to get the page id. :/
      const postDetailUrl = new URL(wagtailApiUrl.href);
      postDetailUrl.searchParams.set("type", "cast.Post");
      postDetailUrl.searchParams.set("slug", postSlug);
      postDetailUrl.searchParams.set("fields", "html_detail,comments");

      try {
        const posts = await dataStore.fetchJson(postDetailUrl);
        post.value = posts.items[0];
      } catch (error) {
        console.error('Error fetching data from API: ', error);
      } finally {
        isLoading.value = false;
      }
    }

    onMounted(fetchPostFromAPI);
    return { dataStore, isLoading, post, visibleDate: visibleDateStr };
  },
}
</script>
