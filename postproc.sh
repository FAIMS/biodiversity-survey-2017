#!/usr/bin/env bash

cd module

string="
        <select1 ref=\"Entity_Types\">
          <label>\{Entity_Types\}<\/label>
          <item>
            <label>Options not loaded<\/label>
            <value>Options not loaded<\/value>
          <\/item>
        <\/select1>"
replacement="
        <group ref=\"Colgroup_1\" faims_style=\"orientation\">
          <label\/>
          <group ref=\"Col_0\" faims_style=\"even\">
            <label\/>
            <select1 ref=\"Entity_Types\">
              <label>\{Entity_Types\}<\/label>
              <item>
                <label>Options not loaded<\/label>
                <value>Options not loaded<\/value>
              <\/item>
            <\/select1>
          <\/group>
          <group ref=\"Col_1\" faims_style=\"even\">
            <label\/>
            <select1 ref=\"Select_User\">
              <label>\{Select_User\}<\/label>
              <item>
                <label>Options not loaded<\/label>
                <value>Options not loaded<\/value>
              <\/item>
            <\/select1>
          <\/group>
          <group ref=\"Col_2\" faims_style=\"even\">
            <label\/>
            <select1 ref=\"Select_Date\">
              <label>\{Select_Date\}<\/label>
              <item>
                <label>Options not loaded<\/label>
                <value>Options not loaded<\/value>
              <\/item>
            <\/select1>
          <\/group>
        <\/group>"
perl -0777 -i.original -pe "s/$string/$replacement/igs" ui_schema.xml

string="
              <Entity_Types\/>"
replacement="
              <Colgroup_1>
                <Col_0>
                  <Entity_Types\/>
                <\/Col_0>
                <Col_1>
                  <Select_User\/>
                <\/Col_1>
                <Col_2>
                  <Select_Date\/>
                <\/Col_2>
              <\/Colgroup_1>"
perl -0777 -i.original -pe "s/$string/$replacement/igs" ui_schema.xml

string="
              <Colgroup_(\\d)>
                <Col_1>
                  <Northing\/>
                <\/Col_1>
                <Col_2>
                  <Easting\/>
                <\/Col_2>
                <Col_3>
                  <Accuracy\/>
                <\/Col_3>
              <\/Colgroup_\\1>"
replacement=""
perl -0777 -i.original -pe "s/$string/$replacement/igs" ui_schema.xml

string="
        <group ref=\"Colgroup_\\d\" faims_style=\"orientation\">
          <label\/>
          <group ref=\"Col_1\" faims_style=\"even\">
            <label\/>
            <input faims_attribute_name=\"Northing\" faims_attribute_type=\"measure\" ref=\"Northing\" faims_read_only=\"true\">
              <label>\\{Northing}<\/label>
            <\/input>
          <\/group>
          <group ref=\"Col_2\" faims_style=\"even\">
            <label\/>
            <input faims_attribute_name=\"Easting\" faims_attribute_type=\"measure\" ref=\"Easting\" faims_read_only=\"true\">
              <label>\\{Easting}<\/label>
            <\/input>
          <\/group>
          <group ref=\"Col_3\" faims_style=\"even\">
            <label\/>
            <input faims_attribute_name=\"Accuracy\" faims_attribute_type=\"measure\" ref=\"Accuracy\" faims_read_only=\"true\">
              <label>\\{Accuracy}<\/label>
            <\/input>
          <\/group>
        <\/group>"
replacement=""
perl -0777 -i.original -pe "s/$string/$replacement/igs" ui_schema.xml

string="
    <property name=\"Northing\" type=\"measure\">
      <description><\/description>
      <formatString>\{\{if \\\$1 then \\\$1}}\{\{if and\(\\\$1, \\\$2\) then \" \" }}\{\{if \\\$2 then \\\$2}}\{\{if \\\$3 then \" \(\\\$3\)\"}}\{\{if between\(\\\$4,0,0.49\) then \"\?\?\" elsif lessThan\(\\\$4,1\) then \"\?\" }}<\/formatString>
      <appendCharacterString> - <\/appendCharacterString>
    <\/property>"
replacement=""
perl -0777 -i.original -pe "s/$string/$replacement/igs" data_schema.xml

string="
    <property name=\"Easting\" type=\"measure\">
      <description><\/description>
      <formatString>\{\{if \\\$1 then \\\$1}}\{\{if and\(\\\$1, \\\$2\) then \" \" }}\{\{if \\\$2 then \\\$2}}\{\{if \\\$3 then \" \(\\\$3\)\"}}\{\{if between\(\\\$4,0,0.49\) then \"\?\?\" elsif lessThan\(\\\$4,1\) then \"\?\" }}<\/formatString>
      <appendCharacterString> - <\/appendCharacterString>
    <\/property>"
replacement=""
perl -0777 -i.original -pe "s/$string/$replacement/igs" data_schema.xml

cat << EOF >> english.0.properties
Select_User=Select User
Select_Date=Select Date
EOF

cat << EOF >> ui_styling.css
.tracklog-start { background-color: green;  }
.tracklog-stop  { background-color: orange; }
EOF

rm   ui_schema.xml.original
rm data_schema.xml.original

cd ../tests

cat << EOF >> mock.bsh
void removeActionBarItem(String name) { return; }
EOF
