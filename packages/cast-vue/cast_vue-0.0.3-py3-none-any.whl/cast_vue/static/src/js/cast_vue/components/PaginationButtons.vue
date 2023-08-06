<template>
    <div class="pagination">
        <button @click="prevPage" :disabled="isFirstPage">&laquo; Prev</button>
        <span>Page {{ currentPage }} of {{ totalPages }}</span>
        <button @click="nextPage" :disabled="isLastPage">Next &raquo;</button>
    </div>
</template>

<script lang="ts">
import { defineComponent, PropType } from 'vue';

export default defineComponent({
    name: 'PaginationButtons',
    props: {
        currentPage: {
            type: Number,
            required: true,
        },
        totalPages: {
            type: Number,
            required: true,
        },
    },
    computed: {
        isFirstPage(): boolean {
            return this.currentPage <= 1;
        },
        isLastPage(): boolean {
            return this.currentPage >= this.totalPages;
        },
    },
    methods: {
        prevPage() {
            if (!this.isFirstPage) {
                this.$emit('change-page', -1);
            }
        },
        nextPage() {
            if (!this.isLastPage) {
                this.$emit('change-page', 1);
            }
        },
    },
});
</script>

<style scoped>
.pagination {
    /* add your styles here */
}
</style>
