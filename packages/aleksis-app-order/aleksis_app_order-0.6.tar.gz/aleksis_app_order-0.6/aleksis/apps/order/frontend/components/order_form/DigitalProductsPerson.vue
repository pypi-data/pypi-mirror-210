<template>
  <main-container>
    <v-card :loading="$apollo.queries.data.loading">
      <v-card-title class="text-h4">
        {{ $t("order.digital_products.my_digital_products") }}
      </v-card-title>
      <v-card-text v-if="data">
        <div v-for="item in data" :key="item.order.id" class="mb-2">
          <h2 class="text-h5 mb-2 black--text">{{ item.order.form.title }}</h2>
          <digital-products-by-order
            :data="item"
            @share-created="shareCreated"
          ></digital-products-by-order>
        </div>
      </v-card-text>
    </v-card>
  </main-container>
</template>

<script>
import MainContainer from "./MainContainer.vue";
import DigitalProductsByOrder from "./DigitalProductsByOrder.vue";
import gqlDigitalProductsPerson from "./digitalProductsPerson.graphql";

export default {
  name: "DigitalProducts",
  components: { DigitalProductsByOrder, MainContainer },
  methods: {
    shareCreated() {
      this.$apollo.queries.data.refetch();
    },
  },
  apollo: {
    data: {
      query: gqlDigitalProductsPerson,
    },
  },
};
</script>
