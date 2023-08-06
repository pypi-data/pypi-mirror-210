export function getTexContentFromElement(
  elementId: string,
  htmlString?: string
): string {
  let dom;
  if (htmlString) {
    const parser = new DOMParser();
    dom = parser.parseFromString(htmlString, "text/html");
  } else {
    dom = document;
  }

  const element = dom.getElementById(elementId);
  if (element === null || element.textContent === null) {
    throw new Error(`Could not find element with id "${elementId}"`);
  }
  return JSON.parse(element.textContent);
}

export function getWagtailApiBaseUrl(): URL {
  const blogPk = getTexContentFromElement("blog-pk");
  const wagtailApiUrlString = getTexContentFromElement("wagtail-api-pages-url");
  const wagtailApiUrl = new URL(wagtailApiUrlString);
  wagtailApiUrl.searchParams.set("child_of", blogPk);
  return wagtailApiUrl;
}


export function getFacetCountsApiBaseUrl(): URL {
  const apiFacetCountsStr = getTexContentFromElement("api-facet-counts-url");
  const apiFacetCountsUrl = new URL(apiFacetCountsStr);
  return apiFacetCountsUrl;
}
