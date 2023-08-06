<template>
    <button @click="count++">{{count}}</button>
</template>

<script>
export default {
  data() {
    return {
      count: 23,
      //count: JSON.parse(document.getElementById("initial-value").textContent),
    };
  },
};
</script>
