<template>
  <main-container>
    <v-card :loading="$apollo.queries.data.loading">
      <v-card-title class="text-h5 grey--text pb-0" v-if="data">{{
        data.order.form.title
      }}</v-card-title>
      <v-card-title class="text-h4">
        {{ $t("order.digital_products.my_digital_products") }}
        <span class="grey--text ml-2" v-if="data">#{{ data.order.id }}</span>
      </v-card-title>
      <v-card-text>
        <digital-products-by-order
          v-if="data"
          :data="data"
          @share-created="shareCreated"
        ></digital-products-by-order>
        <div v-if="data" v-html="data.order.form.helpText" />
      </v-card-text>
    </v-card>
  </main-container>
</template>

<script>
import MainContainer from "./MainContainer.vue";
import DigitalProductsByOrder from "./DigitalProductsByOrder.vue";
import gqlDigitalProducts from "./digitalProducts.graphql";

export default {
  name: "DigitalProducts",
  components: {
    DigitalProductsByOrder,
    MainContainer,
  },
  methods: {
    shareCreated() {
      this.$apollo.queries.data.refetch();
    },
  },
  apollo: {
    data: {
      query: gqlDigitalProducts,
      variables() {
        return {
          key: this.$route.params.key,
        };
      },
    },
  },
};
</script>
