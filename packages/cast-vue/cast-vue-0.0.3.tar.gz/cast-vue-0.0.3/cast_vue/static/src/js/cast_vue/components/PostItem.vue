<template>
  <div class="post-item">
    <h2>{{ post.title }}</h2>
    <div v-if="detail">
      <p>
        <time :date-time="visibleDateTimeStr">{{ visibleDate }}</time>, by
        <span class="author">{{ author }}</span>
      </p>
    </div>
    <div v-else>
      visible date detail
      <p>
        <router-link :to="{ name: 'PostDetail', params: { slug: post.meta.slug } }">
          <time :date-time="visibleDateTimeStr">{{ visibleDate }}</time> </router-link>, by
        <span class="author">{{ author }}</span>
      </p>
    </div>
    <div v-if="detail" v-html="post.html_detail" @click="handleClick"></div>
    <div v-else v-html="post.html_overview" @click="handleClick"></div>
    <div v-if="post.comments" class="comments">
      <comment-list :comments="post.comments"></comment-list>
    </div>
    <div v-if="isModalOpen" id="modal-div" class="modal" @click="handleModalClick">
      <span class="close" @click="closeModal">&times;</span>
      <img id="modal-image" class="modal-content" :src="modalImage.src" :srcset="modalImage.srcset"
        :next="modalImage.next" :prev="modalImage.prev" alt="Full-sized image" />
    </div>
  </div>
</template>

<script lang="ts">
import { getTexContentFromElement } from "../helpers/dom";
import { Post, ModalImage } from "./types";
import CommentList from "./CommentList.vue";


export default {
  mounted() {
    // Add event listener when the component is mounted
    window.addEventListener("keydown", this.handleKeyDown);
  },
  beforeUnmount() {
    // Remove event listener when the component is unmounted
    window.removeEventListener("keydown", this.handleKeyDown);
  },
  name: "PostItem",
  components: {
    CommentList,
  },
  props: {
    post: {
      type: Object as () => Post,
      required: true,
    },
    detail: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      isModalOpen: false,
      modalImage: {} as ModalImage,
    };
  },
  methods: {
    handleClick(e: Event) {
      // console.log("handleClick: ", e);
      if (!e.target) {
        return;
      }
      const clickedEl = e.target as HTMLImageElement;
      if (!(clickedEl.id)) {
        return;
      }
      if (!clickedEl.id.startsWith("gallery-image")) {
        return;
      }
      this.setModalFromImage(clickedEl);
    },
    setModalFromImage(clickedEl: HTMLImageElement) {
      const prev = clickedEl.getAttribute("data-prev");
      if (!prev) {
        return;
      }
      this.modalImage.prev = prev;
      const next = clickedEl.getAttribute("data-next");
      if (!next) {
        return;
      }
      this.modalImage.next = next;
      const fullSrc = clickedEl.getAttribute("data-fullsrc");
      if (!fullSrc) {
        return;
      }
      this.modalImage.src = fullSrc;
      const srcset = clickedEl.getAttribute("data-srcset");
      if (!srcset) {
        return;
      }
      this.modalImage.srcset = srcset;
      this.isModalOpen = true;
    },
    closeModal() {
      this.isModalOpen = false;
    },
    handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        this.closeModal();
      } else if (event.key === "ArrowLeft") {
        if (!this.isModalOpen || !this.modalImage.prev) {
          return;
        }
        const imageId = this.modalImage.prev.split("-")[1]
        const prevImage = document.getElementById("gallery-image-" + imageId) as HTMLImageElement;
        if (!prevImage) {
          return;
        }
        this.setModalFromImage(prevImage);
      } else if (event.key === "ArrowRight") {
        if (!this.isModalOpen || !this.modalImage.next) {
          return;
        }
        const imageId = this.modalImage.next.split("-")[1]
        const nextImage = document.getElementById("gallery-image-" + imageId) as HTMLImageElement;
        if (!nextImage) {
          return;
        }
        this.setModalFromImage(nextImage);
      }

    },
    handleModalClick(e: Event) {
      if (!e.target) {
        return;
      }
      const clickedEl = e.target as HTMLElement;
      // console.log("handleModalClick: ", clickedEl.id);
      if (clickedEl.id === "modal-div") {
        this.closeModal();
      } else if (clickedEl.id === "modal-image") {
        window.open(this.modalImage.src, '_blank');
      }
    }
  },
  computed: {
    visibleDate(): string {
      const visibleDateStr = getTexContentFromElement(
        "vue-article-date",
        this.post.html_detail
      );
      return visibleDateStr;
    },
    visibleDateTimeStr(): string {
      const visibleDateTimeStr = getTexContentFromElement(
        "vue-article-datetime",
        this.post.html_detail
      );
      return visibleDateTimeStr;
    },
    author(): string {
      const author = getTexContentFromElement(
        "vue-article-author",
        this.post.html_detail
      );
      return author;
    },
  },
};
</script>

<style scoped>
.modal {
  display: flex;
  justify-content: center;
  align-items: center;
  position: fixed;
  z-index: 1;
  left: 0;
  top: 0;
  width: 100%;
  height: 100%;
  overflow: auto;
  background-color: rgba(0, 0, 0, 0.6);
}

.modal-content {
  margin: auto;
  display: block;
  width: 80%;
  max-width: 900px;
  max-height: 740px;
  object-fit: contain;
}

.close {
  position: absolute;
  top: 15px;
  right: 35px;
  color: #f1f1f1;
  font-size: 40px;
  font-weight: bold;
  transition: 0.3s;
}

.close:hover,
.close:focus {
  color: #bbb;
  text-decoration: none;
  cursor: pointer;
}
</style>
