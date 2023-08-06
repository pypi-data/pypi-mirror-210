<template>
  <v-row>
    <v-col
      cols="9"
      md="10"
      lg="10"
      xl="10"
      class="text-h5 font-weight-bold d-flex align-center"
    >
      <div class="mr-2">{{ $t("order.items.total") }}</div>
      <div class="text-body-1 font-weight-regular text--secondary">
        ({{ $tc("order.items.items_count", totalCount) }})
      </div>
    </v-col>
    <v-col cols="3" md="2" lg="2" xl="2" class="d-flex justify-end">
      <div class="text-right text-h5 font-weight-bold">
        {{ totalWithCurrency }}
      </div>
    </v-col>
  </v-row>
</template>

<script>
import { formatCurrency } from "./util";

export default {
  name: "TotalRow",
  computed: {
    totalWithCurrency() {
      return formatCurrency(this.total);
    },
  },
  props: {
    total: {
      type: Number,
      required: true,
    },
    totalCount: {
      type: Number,
      required: true,
    },
  },
};
</script>

<style scoped></style>
