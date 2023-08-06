import { shallowMount } from "@vue/test-utils";
import CommentList from "../../cast_vue/static/src/js/cast_vue/components/CommentList.vue";
import { Comment } from "../../cast_vue/static/src/js/cast_vue/components/types";

describe("CommentList.vue", () => {
  it("renders comment list", () => {
    const comments: Comment[] = [
      {
        id: 1,
        parent: null,
        user: "User1",
        date: "2023-05-26",
        comment: "Hello World",
      },
      {
        id: 2,
        parent: 1,
        user: "User2",
        date: "2023-05-27",
        comment: "Hello back",
      },
    ];

    const wrapper = shallowMount(CommentList, {
      props: { comments },
    });

    expect(wrapper.findAllComponents({ name: "CommentItem" })).toHaveLength(1);
  });
});
