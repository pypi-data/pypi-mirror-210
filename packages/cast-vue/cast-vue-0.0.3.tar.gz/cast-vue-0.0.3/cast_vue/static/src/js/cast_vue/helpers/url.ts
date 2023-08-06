// Helper function to update URL's search parameters
export const setUrlSearchParams = (url: URL, params: Record<string, any>) => {
  Object.keys(params).forEach((key) => {
    const value = params[key];
    if (value === "" || value === null || value === undefined) {
      url.searchParams.delete(key);
    } else {
      url.searchParams.set(key, params[key]);
    }
  });
};

// Helper function to get URL's search parameters as an object
export const getUrlSearchParams = (
  query: Record<string, any>
): Record<string, string> => {
  let result: Record<string, string> = {};
  Object.keys(query).forEach((key) => {
    result[key] = query[key] as string;
  });
  return result;
};
