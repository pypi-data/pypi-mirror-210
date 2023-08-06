<template>
    <form @submit.prevent="submitForm">
      <p>
        <label for="id_search">Search:</label>
        <input v-model="form.search" id="id_search" />
      </p>
      <p>
        <label>Date:</label>
        <input type="date" v-model="form.date_after" placeholder="YYYY/MM/DD" id="id_date_0">
        -
        <input type="date" v-model="form.date_before" placeholder="YYYY/MM/DD" id="id_date_1">
      </p>
      <p>
        <label for="id_date_facets">Date Facets:</label>
        <input v-model="form.date_facets" id="id_date_facets" />
        <div class="cast-date-facet-container" id="id_date_facets">
          <div class="cast-date-facet-item">
            <a class="selected" href="#" @click.prevent="selectDateFacet('')">All</a>
          </div>
          <div v-for="(count, facet) in facetCounts" :key="facet" class="cast-date-facet-item">
            <a href="#" @click.prevent="selectDateFacet(facet)">{{ facet }} ({{ count }})</a>
          </div>
        </div>
      </p>
      <p>
        <label for="id_o">Ordering:</label>
        <select v-model="form.order" name="order" id="id_o">
          <option value="">---------</option>
          <option value="visible_date">Date</option>
          <option value="-visible_date">Date (descending)</option>
        </select>
      </p>
      <button type="submit">Filter</button>
    </form>
  </template>

  <script lang="ts">
  import { ref, watchEffect } from 'vue';
  import { Form } from './types';


  export default {
    props: {
      form: {
        type: Object as () => Form,
        default: () => ({}),
      },
      facetCounts: {
        type: Object,
        default: () => ({}),
      },
    },
    setup(props, context) {
      const form = ref<Form>(props.form);

      watchEffect(() => {
        // Update the ref whenever the prop changes
        form.value = props.form;
      });

      const submitForm = () => {
        // handle form submission here
        console.log(form.value);
        context.emit("submitFilterForm", form.value);
      };

      const selectDateFacet = (month: string) => {
        form.value.date_facets = month;
        context.emit("submitFilterForm", form.value);
      };

      return { form, submitForm, selectDateFacet };
    },
    emits: ["submitFilterForm"],
  };
  </script>
