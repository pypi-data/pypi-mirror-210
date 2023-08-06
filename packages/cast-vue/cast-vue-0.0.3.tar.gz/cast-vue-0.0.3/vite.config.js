import vue from "@vitejs/plugin-vue";

const { resolve } = require("path");

module.exports = {
  plugins: [vue()],
  root: resolve("./cast_vue/static/src"),
  base: "/static/",
  server: {
    host: "0.0.0.0",
    port: 3000,
    open: false,
    watch: {
      usePolling: true,
      disableGlobbing: false,
    },
  },
  resolve: {
    extensions: [".js", ".json", ".ts"],
  },
  build: {
    outDir: resolve("./cast_vue/static/cast_vue"),
    assetsDir: "",
    manifest: true,
    emptyOutDir: true,
    target: "es2015",
    rollupOptions: {
      input: {
        main: resolve("./cast_vue/static/src/js/cast_vue/main.ts"),
      },
      output: {
        chunkFileNames: undefined,
      },
    },
  },
};
