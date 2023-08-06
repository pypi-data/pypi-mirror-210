<template>
    <div class="comment">
        <div class="comment-user">{{ comment.user }}</div>
        <div class="comment-date">{{ comment.date }}</div>
        <div class="comment-body">{{ comment.comment }}</div>
        <button @click="showReplyForm = !showReplyForm">Reply</button>
        <div v-if="showReplyForm">
            <textarea v-model="replyText" placeholder="Write a reply..."></textarea>
            <button @click="submitReply">Submit</button>
        </div>
        <div class="comment-children" v-if="hasChildren">
            <div v-for="child in children" :key="child.id">
                <comment-item :comment="child" :comments="comments" />
            </div>
        </div>
    </div>
</template>

<script lang="ts">
import { computed, defineComponent, PropType, ref } from 'vue';
import { Comment } from './types';

export default defineComponent({
    name: 'CommentItem',
    props: {
        comment: {
            type: Object as PropType<Comment>,
            required: true,
        },
        comments: {
            type: Array as PropType<Comment[]>,
            required: true,
        },
    },
    setup(props) {
        const replyText = ref('');
        const showReplyForm = ref(false);
        const children = computed(() =>
            props.comments.filter((c) => c.parent === props.comment.id)
        );
        const hasChildren = computed(() => children.value.length > 0);

        const submitReply = () => {
            console.log('Submit reply:', replyText.value);
            // Add your logic here to submit the reply
            replyText.value = '';
            showReplyForm.value = false;
        };

        return {
            replyText,
            showReplyForm,
            submitReply,
            children,
            hasChildren,
        };
    },
});
</script>
<style scoped>
.comment {
    border: 1px solid #ddd;
    padding: 10px;
    margin-bottom: 10px;
}

.comment-user {
    font-weight: bold;
}

.comment-date {
    color: #888;
    font-size: 0.8em;
}

.comment-children {
    margin-left: 20px;
}</style>
