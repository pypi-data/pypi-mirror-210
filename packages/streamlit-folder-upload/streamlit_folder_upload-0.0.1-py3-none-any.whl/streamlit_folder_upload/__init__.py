import os
import streamlit.components.v1 as components

_RELEASE = True


if not _RELEASE:
    _component_func = components.declare_component(
        "folder_upload_field",
        url="http://localhost:3001",
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _component_func = components.declare_component(
        "folder_upload_field", path=build_dir
    )


def folder_upload_field(
    name: str,
    websocket_url: str,
    auth_token: str,
    project_id: str,
    sub_index: str,
    chunk_size: str,
    key=None,
):
    file_list = _component_func(
        name=name,
        websocket_url=websocket_url,
        auth_token=auth_token,
        project_id=project_id,
        sub_index=sub_index,
        chunk_size=chunk_size,
        key=key,
        default=[],
    )
    return file_list


# if not _RELEASE:
#    import streamlit as st

#    st.subheader("Component with constant args")
#    files = folder_upload_field(
#        name="test",
#        websocket_url="ws://localhost:8010/project-manager/file-upload",
#    )
