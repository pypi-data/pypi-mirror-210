export interface Comment {
  id: number;
  parent: number | null;
  user: string;
  date: string;
  comment: string;
}

export interface Post {
  id: number;
  title: string;
  visible_date: string;
  html_overview: string;
  html_detail: string;
  comments: [Comment];
  meta: {
    type: string;
    detail_url: string;
    html_url: string;
    slug: string;
    first_published_at: string;
  };
}

export interface PostsFromApi {
  meta: {
    total_count: number;
  };
  items: [Post];
}

export interface ModalImage {
  src: string;
  srcset: string;
  next: string;
  prev: string;
}

export interface Form {
  search: string;
  date_after: string;
  date_before: string;
  date_facets: string;
  order: string;
}
