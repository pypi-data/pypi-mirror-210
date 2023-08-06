import { shallowMount } from "@vue/test-utils";
import CommentItem from "../../cast_vue/static/src/js/cast_vue/components/CommentItem.vue";
import { Comment } from "../../cast_vue/static/src/js/cast_vue/components/types";


describe("CommentItem.vue", () => {
  it("renders comment item", () => {
    const comment: Comment = {
      id: 1,
      parent: null,
      user: "User1",
      date: "2023-05-26",
      comment: "Hello World",
    };
    const comments: Comment[] = [
      comment,
      {
        id: 2,
        parent: 1,
        user: "User2",
        date: "2023-05-27",
        comment: "Hello back",
      },
    ];

    const wrapper = shallowMount(CommentItem, {
      props: { comment, comments },
    });

    expect(wrapper.text()).toContain("User1");
    expect(wrapper.text()).toContain("Hello World");
    expect(wrapper.findAllComponents({ name: "CommentItem" })).toHaveLength(1);
  });

  it("shows reply form when reply button is clicked", async () => {
    const comment: Comment = {
      id: 1,
      parent: null,
      user: "User1",
      date: "2023-05-26",
      comment: "Hello World",
    };
    const comments: Comment[] = [comment];

    const wrapper = shallowMount(CommentItem, {
      props: { comment, comments },
    });

    expect(wrapper.vm.showReplyForm).toBe(false);
    await wrapper.find("button").trigger("click");
    expect(wrapper.vm.showReplyForm).toBe(true);
  });
});
