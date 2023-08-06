<template>
    <div class="comment-list">
        <div v-for="comment in rootComments" :key="comment.id">
            <comment-item :comment="comment" :comments="comments" />
        </div>
        <textarea v-model="newCommentText" placeholder="Add a comment..."></textarea>
        <button @click="submitNewComment">Submit</button>
    </div>
</template>

<script lang="ts">
import { defineComponent, PropType, ref, computed } from 'vue';
import CommentItem from './CommentItem.vue';
import { Comment } from './types';

export default defineComponent({
    components: {
        CommentItem,
    },
    props: {
        comments: {
            type: Array as PropType<Comment[]>,
            required: true,
        },
    },
    setup(props) {
        const newCommentText = ref('');
        const rootComments = computed(() =>
            props.comments.filter((comment) => comment.parent === null)
        );

        const submitNewComment = () => {
            console.log('Submit new comment:', newCommentText.value);
            // Add your logic here to submit the new comment
            newCommentText.value = '';
        };

        return {
            newCommentText,
            submitNewComment,
            rootComments,

        }
    }
});
</script>
<style scoped>
.comment-list {
  margin: 0;
  padding: 0;
  list-style: none;
}
</style>
