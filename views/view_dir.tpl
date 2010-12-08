%include header title=path, js=['view_dir.js']
{{!crumbs}}
%for entry in entries:
  <li>{{!entry}}</li>
%end
</ul>
%include footer
