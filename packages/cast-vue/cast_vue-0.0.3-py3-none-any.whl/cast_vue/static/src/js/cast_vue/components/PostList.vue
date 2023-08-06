<template>
  <div>
    <h1>{{ blog.title }}</h1>
    <p v-html="blog.description"></p>
    <div v-for="post in posts.items" :key="post.id">
      <post-item :post="post" :detail="false"></post-item>
    </div>
  </div>
</template>

<script lang="ts">
import { useDataStore } from '../stores/dataStore';
import PostItem from './PostItem.vue';
import { PostsFromApi } from './types';

export default {
  name: "PostList",
  components: {
    PostItem,
  },
  props: {
    posts: {
      type: Object as () => PostsFromApi,
      default: () => ({}),
    },
    blog: {
      type: Object,
      default: () => ({}),
    }
  },
  setup() {
    const dataStore = useDataStore();
    return {
      dataStore,
    };
  }
}
</script>
