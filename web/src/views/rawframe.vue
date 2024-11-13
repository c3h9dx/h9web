<script setup>

import {CCardBody} from "@coreui/vue/dist/esm/components/card/index.js";
import {CCol} from "@coreui/vue/dist/esm/components/grid/index.js";
</script>

<template>
  <div>
  <CCard>
    <CCardBody>
      <CForm class="row g-3">
        <!--      <div class="row align-items-center justify-content-center">-->
        <!--        <div class="col col-auto">-->
        <CCol class="col-auto">
          <CFormLabel for="inputPriority">Priority</CFormLabel>
          <CFormSelect id="inputPriority" size="sm"></CFormSelect>
        </CCol>
        <!--          <select [(ngModel)]="frame.priority" id="inputPriority" name="priority" size="1"-->
        <!--                  class="form-control custom-select">-->
        <!--            <option *ngFor="let p of Priority" [ngValue]="p.id">{{ p.name }}</option>-->
        <!--          </select>-->
        <!--        </div>-->
        <!--        <div class="col col-auto">-->
        <CCol class="col-auto">
          <CFormLabel for="inputType">Type</CFormLabel>
          <CFormSelect id="inputType" size="sm"></CFormSelect>
        </CCol>
        <!--          <select [(ngModel)]="frame.type" id="inputType" name="type" class="form-control custom-select">-->
        <!--            <option *ngFor="let t of Type" [ngValue]="t.id">{{ t.name }}</option>-->
        <!--          </select>-->
        <!--        </div>-->
        <!--        <div class="col col-auto">-->
        <CCol class="col-auto">
          <CFormLabel for="inputSeqnum">Seqnum</CFormLabel>
          <CFormInput id="inputSeqnum" size="sm"></CFormInput>
        </CCol>
        <!--          <input [disabled]="!raw_frame" [(ngModel)]="frame.seqnum" type="number" name="seqnum" class="form-control"-->
        <!--                 id="inputSeqnum" min="0"-->
        <!--                 max="31" size="2">-->
        <!--        </div>-->
        <!--        <div class="col col-auto">-->
        <!--          <label for="inputSource">Source</label>-->
        <CCol class="col-auto">
          <CFormLabel for="inputSource">Source</CFormLabel>
          <CFormInput id="inputSource" size="sm"></CFormInput>
        </CCol>
        <!--          <input [disabled]="!raw_frame" [(ngModel)]="frame.source_id" type="number" name="source" class="form-control"-->
        <!--                 id="inputSource" min="0"-->
        <!--                 max="511" size="3"-->
        <!--                 value="0">-->
        <!--        </div>-->
        <!--        <div class="col col-auto">-->
        <!--          <label for="inputDestination">Destination</label>-->
        <CCol class="col-auto">
          <CFormLabel for="inputDestination">Destination</CFormLabel>
          <CFormInput id="inputDestination" size="sm"></CFormInput>
        </CCol>
        <!--          <input [(ngModel)]="frame.destination_id" type="number" name="destination" class="form-control"-->
        <!--                 id="inputDestination" min="0" max="511"-->
        <!--                 size="3" value="0">-->
        <!--        </div>-->
        <!--        <div class="col col-auto">-->
        <CCol class="col-auto">
          <CFormLabel for="inputData">Data</CFormLabel>
          <fieldset id="inputData">
            <CInputGroup>
              <CFormInput name="data[0]" size="sm" maxlength="2"></CFormInput>
              <!--              <input [(ngModel)]="frame.data[0]" name="data[0]" type="text" class="form-control" size="2" maxlength="2"-->
              <!--                     placeholder="">-->
              <CFormInput name="data[1]" size="sm" maxlength="2"></CFormInput>
              <!--              <input [(ngModel)]="frame.data[1]" name="data[1]" type="text" class="form-control" size="2" maxlength="2"-->
              <!--                     placeholder="">-->
              <CFormInput name="data[2]" size="sm" maxlength="2"></CFormInput>
              <!--              <input [(ngModel)]="frame.data[2]" name="data[2]" type="text" class="form-control" size="2" maxlength="2"-->
              <!--                     placeholder="">-->
              <CFormInput name="data[3]" size="sm" maxlength="2"></CFormInput>
              <!--              <input [(ngModel)]="frame.data[3]" name="data[3]" type="text" class="form-control" size="2" maxlength="2"-->
              <!--                     placeholder="">-->
              <CFormInput name="data[4]" size="sm" maxlength="2"></CFormInput>
              <!--              <input [(ngModel)]="frame.data[4]" name="data[4]" type="text" class="form-control" size="2" maxlength="2"-->
              <!--                     placeholder="">-->
              <CFormInput name="data[5]" size="sm" maxlength="2"></CFormInput>
              <!--              <input [(ngModel)]="frame.data[5]" name="data[5]" type="text" class="form-control" size="2" maxlength="2"-->
              <!--                     placeholder="">-->
              <CFormInput name="data[6]" size="sm" maxlength="2"></CFormInput>
              <!--              <input [(ngModel)]="frame.data[6]" name="data[6]" type="text" class="form-control" size="2" maxlength="2"-->
              <!--                     placeholder="">-->
              <CFormInput name="data[7]" size="sm" maxlength="2"></CFormInput>
              <!--              <input [(ngModel)]="frame.data[7]" name="data[7]" type="text" class="form-control" size="2" maxlength="2"-->
              <!--                     placeholder="">-->
            </CInputGroup>
          </fieldset>
        </CCol>
        <!--        </div>-->
        <!--      </div>-->
        <!--      <div class="row justify-content-end mt-2">-->
        <!--        &lt;!&ndash;      <div class="col"></div>&ndash;&gt;-->
        <!--        <div class="col col-auto">-->
        <!--          &lt;!&ndash;      {% module xsrf_form_html() %}&ndash;&gt;-->
        <!--          <label for="raw_checkbox" class="ms-1" title="Allows to set the seqnum and source">-->
        <!--            <input [(ngModel)]="raw_frame" type="checkbox" id="raw_checkbox" name="Raw"/>-->
        <!--            Raw frame-->
        <!--          </label>-->
        <!--          <button (click)="clean_frame(frame)" class="btn btn-primary text-light mb-2 ms-3">Clean</button>-->
        <!--          <button (click)="send_frame(frame)" class="btn btn-primary text-light mb-2 ms-2">-->
        <!--            &lt;!&ndash;          <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>&ndash;&gt;-->
        <!--            Send frame-->
        <!--          </button>-->
        <!--        </div>-->
        <!--      </div>-->
      </CForm>
    </CCardBody>
  </CCard>
  <CCard>
    <CCardBody>
    <CVirtualScroller class="border" :visibleItems="20">
      <div v-for="item in 10000">Option {{ item }}</div>
    </CVirtualScroller>
      </CCardBody>
  </CCard>
  </div>
</template>

<style scoped>

</style>