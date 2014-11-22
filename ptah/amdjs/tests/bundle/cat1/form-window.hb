<div class="modal fade out" data-type="window"
     style="max-height: 10000px; position:absolute">
  <div class="modal-header">
    <a class="close" data-dismiss="modal">×</a>
    <h3>{{label}}</h3>
  </div>
  <div class="modal-body">
    {{#description}}
      <p>{{&description}}</p>
    {{/description}}
    <form class="form-horizontal">
      <div data-place="content">
        {{>globals.form}}
      </div>
    </form>
  </div>
  <div class="modal-footer">
    {{#actions}}
      <a href="#" class="{{cls}}" data-action="{{name}}">{{title}}</a>
    {{/actions}}
  </div>
</div>
