#!/usr/bin/env python
import argparse
import json
import sys
import time
from http import HTTPStatus

import dashscope
from dashscope.aigc import Generation
from dashscope.common.constants import (DeploymentStatus, FilePurpose,
                                        TaskStatus)


def text_generation(args):
    response = Generation.call(args.model, args.prompt, stream=args.stream)
    if args.stream:
        for rsp in response:
            if rsp.status_code == 200:
                print(rsp.output)
    else:
        if response.status_code == 200:
            print(response.output)


class FineTunes:
    @classmethod
    def call(cls, args):
        hyper_parameters = None
        if args.hyper_parameters:
            hyper_parameters = json.loads(args.hyper_parameters)
        rsp = dashscope.FineTune.call(
            model=args.model,
            training_file_ids=args.training_file_ids,
            validation_file_ids=args.validation_file_ids,
            hyper_parameters=hyper_parameters)
        if rsp.status_code == HTTPStatus.OK:
            print('Create fine-tune job success, job_id: %s' %
                  rsp.output['job_id'])
            cls.wait(rsp.output['job_id'])
        else:
            print('Failed, status_code: %s, code: %s, message: %s' %
                  (rsp.status_code, rsp.code, rsp.message))

    @classmethod
    def wait(cls, job_id):
        while True:
            rsp = dashscope.FineTune.get(job_id)
            if rsp.status_code == HTTPStatus.OK:
                if rsp.output['status'] == TaskStatus.FAILED:
                    print('Fine-tune failed!')
                    break
                elif rsp.output['status'] == TaskStatus.CANCELED:
                    print('Fine-tune task canceled')
                    break
                elif rsp.output['status'] == TaskStatus.SUCCEEDED:
                    print('Fine-tune task success, fine-tuned model:%s' %
                          rsp.output['output_model'])
                    break
                else:
                    print('The fine-tune task is: %s' % rsp.output['status'])
                    time.sleep(30)
            else:
                print('Failed, status_code: %s, code: %s, message: %s' %
                      (rsp.status_code, rsp.code, rsp.message))

    @classmethod
    def get(cls, args):
        rsp = dashscope.FineTune.get(args.job)
        if rsp.status_code == HTTPStatus.OK:
            if rsp.output['status'] == TaskStatus.FAILED:
                print('Fine-tune failed!')
            elif rsp.output['status'] == TaskStatus.CANCELED:
                print('Fine-tune task canceled')
            elif rsp.output['status'] == TaskStatus.SUCCEEDED:
                print('Fine-tune task success, fine-tuned model : %s' %
                      rsp.output['output_model'])
            else:
                print('The fine-tune task is: %s' % rsp.output['status'])
        else:
            print('Failed, status_code: %s, code: %s, message: %s' %
                  (rsp.status_code, rsp.code, rsp.message))

    @classmethod
    def list(cls, args):
        rsp = dashscope.FineTune.list()
        if rsp.status_code == HTTPStatus.OK:
            for job in rsp.output['jobs']:
                if job['status'] == TaskStatus.SUCCEEDED:
                    print(
                        'job: %s, status: %s, base model: %s, output model: %s'
                        % (job['job_id'], job['status'], job['model'],
                           job['output_model']))
                else:
                    print('job: %s, status: %s, base model: %s' %
                          (job['job_id'], job['status'], job['model']))

    @classmethod
    def events(cls, args):
        rsp = dashscope.FineTune.stream_events(args.job)
        if rsp.status_code == HTTPStatus.OK:
            print('TODO process result.')

    @classmethod
    def follow(cls, args):
        rsp = dashscope.FineTune.stream_events(args.job)
        if rsp.status_code == HTTPStatus.OK:
            print('TODO support future')

    @classmethod
    def cancel(cls, args):
        rsp = dashscope.FineTune.cancel(args.job)
        if rsp.status_code == HTTPStatus.OK:
            print(rsp.output['message'])


class Files:
    @classmethod
    def upload(cls, args):
        rsp = dashscope.File.upload(file_path=args.file, purpose=args.purpose)
        if rsp.status_code == HTTPStatus.OK:
            print('Upload success, file id: %s' %
                  rsp.output['data']['success_data'][0]['file_id'])
        else:
            print('Upload failed, reason: %s' % rsp.message)

    @classmethod
    def get(cls, args):
        rsp = dashscope.File.get(file_id=args.id)
        if rsp.status_code == HTTPStatus.OK:
            print('file_id: %s, name: %s, description: %s' %
                  (rsp.output['data']['file_id'], rsp.output['data']['name'],
                   rsp.output['data']['description']))
        else:
            print('Get file failed, reason: %s' % rsp.message)

    @classmethod
    def list(cls, args):
        rsp = dashscope.File.list()
        if rsp.status_code == HTTPStatus.OK:
            print('Files')
            for f in rsp.output['data']['files']:
                print('file_id: %s, name: %s, description: %s' %
                      (f['file_id'], f['name'], f['description']))
        else:
            print('List failed, reason: %s' % rsp.message)

    @classmethod
    def delete(cls, args):
        rsp = dashscope.File.delete(args.id)
        if rsp.status_code == HTTPStatus.OK:
            print('Delete success')
        else:
            print('Delete failed, reason: %s' % rsp.message)


class Deployments:
    @classmethod
    def call(cls, args):
        rsp = dashscope.Deployment.call(model=args.model, suffix=args.suffix)
        if rsp.status_code == HTTPStatus.OK:
            deployment_id = rsp.output['deployment_id']
            print('Create deployment id: %s' % deployment_id)
            while True:  # wait for deployment ok.
                status = dashscope.Deployment.get(deployment_id)
                if status.status_code == HTTPStatus.OK:
                    if status.output['status'] == DeploymentStatus.DEPLOYING:
                        time.sleep(30)
                        print('Deployment %s is deploying' % deployment_id)
                    else:
                        print('Deployment: %s status: %s' %
                              (deployment_id, status.output['status']))
                        break

                else:
                    print('Get deployment %s failed, code: %s, message: %s' %
                          (deployment_id, rsp.code, rsp.message))
        else:
            print(('Create deployment failed, status_code: %s, \
                    code: %s, message: %s') %
                  (rsp.status_code, rsp.code, rsp.message))

    @classmethod
    def get(cls, args):
        rsp = dashscope.Deployment.get(args.id)
        if rsp.status_code == HTTPStatus.OK:
            print('Deployment %s status: %s' % (args.id, rsp.output['status']))
        else:
            print('Get failed, status_code: %s, code: %s, message: %s' %
                  (rsp.status_code, rsp.code, rsp.message))

    @classmethod
    def list(cls, args):
        rsp = dashscope.Deployment.list()  # TODO page.
        if rsp.status_code == HTTPStatus.OK:
            if 'deployments' in rsp.output:
                for deployment in rsp.output['deployments']:
                    print('Deployment: %s, model: %s, status: %s' %
                          (deployment['deployment_id'], deployment['model'],
                           deployment['status']))
            else:
                print('There is no deployments!')

    @classmethod
    def delete(cls, args):
        rsp = dashscope.Deployment.delete(args.id)
        if rsp.status_code == HTTPStatus.OK:
            print(rsp.output['message'])
        else:
            print('Delete failed, status_code: %s, code: %s, message: %s' %
                  (rsp.status_code, rsp.code, rsp.message))


def main():
    parser = argparse.ArgumentParser(
        prog='dashscope', description='dashscope command line tools.')
    parser.add_argument('-k', '--api-key', help='Dashscope API key.')
    sub_parsers = parser.add_subparsers(help='Api subcommands')
    text_generation_parser = sub_parsers.add_parser('generation.call')
    text_generation_parser.add_argument('-p',
                                        '--prompt',
                                        required=True,
                                        help='Input prompt')
    text_generation_parser.add_argument('-m',
                                        '--model',
                                        required=True,
                                        help='The model to call.')
    text_generation_parser.add_argument('--history',
                                        required=False,
                                        help='The history of the request.')
    text_generation_parser.add_argument('-s',
                                        '--stream',
                                        default=False,
                                        action='store_true',
                                        help='Use stream mode default false.')
    text_generation_parser.set_defaults(func=text_generation)
    fine_tune_call = sub_parsers.add_parser('fine_tunes.call')
    fine_tune_call.add_argument(
        '-t',
        '--training_file_ids',
        required=True,
        nargs='+',
        help='Training file ids which upload by File command.')
    fine_tune_call.add_argument(
        '-v',
        '--validation_file_ids',
        required=False,
        nargs='+',
        default=[],
        help='Validation file ids which upload by File command.')
    fine_tune_call.add_argument('-m',
                                '--model',
                                required=True,
                                help='The based model to start fine-tune.')
    fine_tune_call.add_argument(
        '-p',
        '--hyper_parameters',
        required=False,
        help='The fine-tune hyper parameters, json string.')
    fine_tune_call.set_defaults(func=FineTunes.call)
    fine_tune_get = sub_parsers.add_parser('fine_tunes.get')
    fine_tune_get.add_argument('-j',
                               '--job',
                               required=True,
                               help='The fine-tune job id.')
    fine_tune_get.set_defaults(func=FineTunes.get)
    fine_tune_list = sub_parsers.add_parser('fine_tunes.list')
    fine_tune_list.set_defaults(func=FineTunes.list)
    fine_tune_cancel = sub_parsers.add_parser('fine_tunes.cancel')
    fine_tune_cancel.add_argument('-j',
                                  '--job',
                                  required=True,
                                  help='The fine-tune job id.')
    fine_tune_cancel.set_defaults(func=FineTunes.cancel)

    file_upload = sub_parsers.add_parser('files.upload')
    file_upload.add_argument(
        '-f',
        '--file',
        required=True,
        help='The file path to upload',
    )
    file_upload.add_argument(
        '-p',
        '--purpose',
        default=FilePurpose.fine_tune,
        const=FilePurpose.fine_tune,
        nargs='?',
        choices=[FilePurpose.fine_tune],
        help='Purpose to upload file[fine-tune]',
        required=True,
    )
    file_upload.set_defaults(func=Files.upload)
    file_get = sub_parsers.add_parser('files.get')
    file_get.add_argument('-i', '--id', required=True, help='The file ID')
    file_get.set_defaults(func=Files.get)
    file_delete = sub_parsers.add_parser('files.delete')
    file_delete.add_argument('-i', '--id', required=True, help='The files ID')
    file_delete.set_defaults(func=Files.delete)
    file_list = sub_parsers.add_parser('files.list')
    file_list.set_defaults(func=Files.list)

    deployments_call = sub_parsers.add_parser('deployments.call')
    deployments_call.add_argument('-m',
                                  '--model',
                                  required=True,
                                  help='The model ID')
    deployments_call.add_argument('-s',
                                  '--suffix',
                                  required=False,
                                  help=('The suffix of the deployment, \
            lower cased characters 8 chars max.'))
    deployments_call.set_defaults(func=Deployments.call)

    deployments_get = sub_parsers.add_parser('deployments.get')
    deployments_get.add_argument('-i',
                                 '--id',
                                 required=True,
                                 help='The deployment ID')
    deployments_get.set_defaults(func=Deployments.get)
    deployments_delete = sub_parsers.add_parser('deployments.delete')
    deployments_delete.add_argument('-i',
                                    '--id',
                                    required=True,
                                    help='The deployment ID')
    deployments_delete.set_defaults(func=Deployments.delete)
    deployments_list = sub_parsers.add_parser('deployments.list')
    deployments_list.set_defaults(func=Deployments.list)

    args = parser.parse_args()
    if args.api_key is not None:
        dashscope.api_key = args.api_key
    args.func(args)


if __name__ == '__main__':
    sys.exit(main())
