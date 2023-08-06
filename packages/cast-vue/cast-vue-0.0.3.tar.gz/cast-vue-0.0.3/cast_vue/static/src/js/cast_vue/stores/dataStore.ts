import { defineStore } from 'pinia';

// Define the store type
interface DataStoreState {
  jsonCache: Record<string, any>;
}

// Define and export the store
export const useDataStore = defineStore({
  id: "main",
  state: (): DataStoreState => ({
    jsonCache: {},
  }),
  actions: {
    async fetchJson(url: URL): Promise<any> {
      // Check if the URL is in the cache.
      const urlStr = url.toString();
      // console.log("fetchJson: ", urlStr)
      if (this.jsonCache[urlStr]) {
        return this.jsonCache[urlStr];
      }

      // Fetch the JSON if it's not in the cache.
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();

      // Store the result in the cache.
      this.jsonCache[urlStr] = data;
      return data;
    },
  },
});
